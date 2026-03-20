from __future__ import annotations

import asyncio
import hashlib
from datetime import date
from typing import Any

from .formatter import ReminderFormatter
from .model import ReminderRequest, ReminderResult
from .usecase import ReminderUseCase, normalize_person_name


def classify_delivery_error(error: Exception) -> dict[str, Any]:
    status_code = getattr(error, "status_code", None)
    if status_code in {408, 425, 429, 500, 502, 503, 504}:
        return {"is_transient": True, "kind": f"http_{status_code}"}
    if status_code in {400, 401, 403, 404}:
        return {"is_transient": False, "kind": f"http_{status_code}"}
    text = str(error).lower()
    transient_tokens = ("timeout", "timed out", "too many requests", "rate limit", "bad gateway", "service unavailable", "gateway timeout", "temporarily")
    if any(token in text for token in transient_tokens):
        return {"is_transient": True, "kind": "message_transient"}
    permanent_tokens = ("chat not found", "forbidden", "bad request", "blocked")
    if any(token in text for token in permanent_tokens):
        return {"is_transient": False, "kind": "message_permanent"}
    return {"is_transient": False, "kind": "unknown"}


class _MockEnhancer:
    async def chat(self, messages: Any, model: str | None = None) -> str | None:  # noqa: ARG002
        if isinstance(messages, str):
            return messages
        if isinstance(messages, list):
            for item in reversed(messages):
                if isinstance(item, dict) and str(item.get("role")) == "user":
                    return str(item.get("content", ""))
        return None


class ReminderJob:
    def __init__(self, *, usecase: ReminderUseCase, formatter: ReminderFormatter, sender: Any, helper_character: str = "", enhancer: Any | None = None, people_lookup: Any | None = None, default_chat_id: str = "", enhance_concurrency: int = 4, send_retry_attempts: int = 3, send_retry_backoff_seconds: float = 0.5, send_retry_backoff_multiplier: float = 2.0, llm_mode: str = "provider", llm_model: str = "", runtime_env: str = "", mock_llm: bool = False) -> None:
        self._usecase = usecase
        self._formatter = formatter
        self._sender = sender
        self._helper_character = str(helper_character or "")
        self._enhancer = _MockEnhancer() if mock_llm else enhancer
        self._people_lookup = people_lookup
        self._default_chat_id = str(default_chat_id or "").strip()
        self._enhance_concurrency = max(1, int(enhance_concurrency))
        self._send_retry_attempts = max(1, int(send_retry_attempts))
        self._send_retry_backoff_seconds = max(0.0, float(send_retry_backoff_seconds))
        self._send_retry_backoff_multiplier = max(1.0, float(send_retry_backoff_multiplier))
        self._llm_mode = str(llm_mode or "provider")
        self._llm_model = str(llm_model or "").strip()
        self._runtime_env = str(runtime_env or "").strip().lower()

    @staticmethod
    def _delivery_key(today: date, owner_name: str, chat_id: str, message: str) -> str:
        message_hash = hashlib.sha256(str(message).encode("utf-8")).hexdigest()[:16]
        return f"{today.isoformat()}|{owner_name}|{chat_id}|{message_hash}"

    async def _enhance_one(self, draft_text: str, semaphore: asyncio.Semaphore) -> tuple[str, str]:
        if self._enhancer is None:
            return draft_text, "fallback_empty"
        if self._llm_mode == "draft_only":
            return draft_text, "skipped_mock"
        async with semaphore:
            try:
                enhanced = await self._enhancer.chat(messages=[{"role": "system", "content": self._helper_character}, {"role": "user", "content": draft_text}], model=(self._llm_model or None))
            except Exception:
                return draft_text, "fallback_exception"
        text = str(enhanced or "").strip()
        if not text:
            return draft_text, "fallback_empty"
        return text, "succeeded"

    async def _send_with_retry(self, *, chat_id: str, message: str, owner_name: str) -> tuple[bool, dict[str, int]]:  # noqa: ARG002
        counters = {"send_errors": 0, "send_retry_attempts": 0, "send_retry_exhausted": 0, "send_error_transient": 0, "send_error_permanent": 0, "send_error_unknown": 0, "sent": 0}
        for attempt in range(1, self._send_retry_attempts + 1):
            try:
                response = await self._sender.send_message(chat_id, message)
                if response is None:
                    raise RuntimeError("telegram_send_returned_none")
                counters["sent"] += 1
                return True, counters
            except Exception as error:
                classification = classify_delivery_error(error)
                transient = bool(classification.get("is_transient", False))
                kind = str(classification.get("kind", "unknown"))
                can_retry = transient and attempt < self._send_retry_attempts
                if can_retry:
                    counters["send_retry_attempts"] += 1
                    delay = self._send_retry_backoff_seconds * (self._send_retry_backoff_multiplier ** (attempt - 1))
                    await asyncio.sleep(delay)
                    continue
                counters["send_errors"] += 1
                if transient:
                    counters["send_error_transient"] += 1
                    if attempt > 1:
                        counters["send_retry_exhausted"] += 1
                elif kind == "unknown":
                    counters["send_error_unknown"] += 1
                else:
                    counters["send_error_permanent"] += 1
                return False, counters
        return False, counters

    async def run(self, req: ReminderRequest) -> ReminderResult:
        groups, today, next_workday = self._usecase.select(req)
        result = ReminderResult(mode=str(req.mode), today=today.isoformat(), next_workday=next_workday.isoformat(), groups=groups, delivery_counters={"candidates_total": 0, "sent": 0, "skipped_no_message": 0, "skipped_no_person": 0, "skipped_no_chat_id": 0, "skipped_vacation": 0, "skipped_mock": 0, "skipped_duplicate": 0, "send_errors": 0, "send_retry_attempts": 0, "send_retry_exhausted": 0, "send_error_transient": 0, "send_error_permanent": 0, "send_error_unknown": 0, "fallback_default_chat": 0}, enhancement_counters={"provider": "mock" if isinstance(self._enhancer, _MockEnhancer) else "llm", "candidates_total": len(groups), "attempted": 0, "succeeded": 0, "fallback_empty": 0, "fallback_exception": 0, "skipped_mock": 0}, warnings=[])
        semaphore = asyncio.Semaphore(self._enhance_concurrency)
        drafts: dict[str, str] = {}
        enhanced_messages: dict[str, str] = {}
        enhance_tasks: dict[str, asyncio.Task[tuple[str, str]]] = {}
        for group in groups:
            draft = self._formatter.build_draft(group, today=today, next_workday=next_workday)
            if draft is None:
                result.delivery_counters["skipped_no_message"] += 1
                continue
            drafts[group.owner_name] = draft.text
            if isinstance(self._enhancer, _MockEnhancer):
                result.enhancement_counters["skipped_mock"] += 1
                enhanced_messages[group.owner_name] = draft.text
            else:
                result.enhancement_counters["attempted"] += 1
                enhance_tasks[group.owner_name] = asyncio.create_task(self._enhance_one(draft.text, semaphore))
        for owner_name, task in enhance_tasks.items():
            message, marker = await task
            enhanced_messages[owner_name] = message
            if marker in result.enhancement_counters:
                result.enhancement_counters[marker] += 1
        result = ReminderResult(artifact=result.artifact, status=result.status, mode=result.mode, today=result.today, next_workday=result.next_workday, groups=result.groups, drafts=drafts, messages={}, delivery_counters=dict(result.delivery_counters), enhancement_counters=dict(result.enhancement_counters), warnings=list(result.warnings))
        people_snapshot = self._people_lookup.get_people_snapshot() if self._people_lookup is not None else None
        people_by_name = dict(getattr(people_snapshot, "people_by_name", {}) or {})
        if not people_by_name:
            result.warnings.append("people_snapshot_missing_or_empty")
        sent_keys: set[str] = set()
        force_test_chat = bool(req.force_test_chat or req.mode == "test" or self._runtime_env == "test")
        test_chat = str(req.test_chat_id_override or self._default_chat_id).strip()
        for owner_name, message in enhanced_messages.items():
            result.delivery_counters["candidates_total"] += 1
            normalized_name = normalize_person_name(owner_name)
            person = people_by_name.get(normalized_name)
            if person is None:
                result.delivery_counters["skipped_no_person"] += 1
                continue
            vacation = str(getattr(person, "vacation", "")).strip().lower()
            if vacation == "да":
                result.delivery_counters["skipped_vacation"] += 1
                continue
            chat_id = test_chat if force_test_chat else str(getattr(person, "chat_id", "")).strip()
            if not chat_id and self._default_chat_id:
                chat_id = self._default_chat_id
                result.delivery_counters["fallback_default_chat"] += 1
            if not chat_id:
                result.delivery_counters["skipped_no_chat_id"] += 1
                continue
            delivery_key = self._delivery_key(today, owner_name, chat_id, message)
            if delivery_key in sent_keys:
                result.delivery_counters["skipped_duplicate"] += 1
                continue
            sent_ok, counters = await self._send_with_retry(chat_id=chat_id, message=message, owner_name=owner_name)
            for key, value in counters.items():
                result.delivery_counters[key] = int(result.delivery_counters.get(key, 0)) + int(value)
            if sent_ok:
                sent_keys.add(delivery_key)
            result.messages[owner_name] = message
        return result

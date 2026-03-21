"""Google LLM adapter boundary."""

from __future__ import annotations

import asyncio
from typing import Any

from core.adapters import LoggerAdapter, NullLogger
from core.reminder_policy import is_transient_llm_error, normalize_chat_messages


class AsyncGoogleLLMChatAgent:
    """Async Google Gemini adapter via Generative Language API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        logger: LoggerAdapter | None = None,
        timeout_seconds: float = 25.0,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.8,
    ) -> None:
        self.api_key = str(api_key or "")
        self.model = str(model or "gemini-2.0-flash")
        self.logger = logger or NullLogger()
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.retry_attempts = max(1, int(retry_attempts))
        self.retry_backoff_seconds = max(0.0, float(retry_backoff_seconds))
        try:
            import httpx
        except Exception as error:
            raise RuntimeError("Optional dep for Google LLM adapter is missing: install `httpx`.") from error
        self.http_client = httpx.AsyncClient(timeout=self.timeout_seconds)

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        normalized = normalize_chat_messages(messages)
        if not normalized:
            return None

        system_parts = [item["content"] for item in normalized if item["role"] == "system"]
        regular_parts = [item["content"] for item in normalized if item["role"] != "system"]
        request_body: dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "\n\n".join(regular_parts)}],
                }
            ]
        }
        if system_parts:
            request_body["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}

        resolved_model = str(model or self.model or "gemini-2.0-flash")
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{resolved_model}:generateContent"
        )
        params = {"key": self.api_key}
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = await self.http_client.post(endpoint, params=params, json=request_body)
                response.raise_for_status()
                payload = response.json()
                candidates = payload.get("candidates") or []
                if not candidates:
                    return None
                parts = ((candidates[0].get("content") or {}).get("parts")) or []
                if not parts:
                    return None
                return str(parts[0].get("text") or "")
            except Exception as error:
                transient = is_transient_llm_error(error)
                can_retry = transient and attempt < self.retry_attempts
                if can_retry:
                    await asyncio.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))
                    continue
                self.logger.log(
                    "Google LLM chat error: "
                    f"attempt={attempt}/{self.retry_attempts} transient={transient} error={error}",
                )
                return None
        return None

    async def aclose(self) -> None:
        await self.http_client.aclose()

"""Reminder pipeline: draft generation, enhancement, and Telegram delivery."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

import aiohttp
import httpx
import pandas as pd
import pytz
from openai import AsyncOpenAI
from telegram.ext import Application

from config import DEFAULT_CHAT_ID, TG
from core.adapters import ChatAdapter, LoggerAdapter, MessageAdapter, NullLogger
from utils.func import filter_stages


def _safe_print(text: Any) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("unicode_escape").decode("ascii"))


def _sanitize_proxy_url(url: str | None) -> str | None:
    if not url:
        return None
    return str(url).strip().strip('"').strip("'")


class TelegramNotifier:
    """Thin adapter for Telegram bot message delivery."""

    def __init__(self, bot_token: str = TG, default_chat_id: str | int = DEFAULT_CHAT_ID) -> None:
        self._bot_token = bot_token
        self._bot = None
        self.default_chat_id = default_chat_id

    def _get_bot(self) -> Any:
        if self._bot is None:
            self._bot = Application.builder().token(self._bot_token).build().bot
        return self._bot

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str | None = "Markdown",
    ) -> Any:
        try:
            bot = self._get_bot()
            return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        except Exception as error:
            _safe_print(f"Ошибка при отправке сообщения в Telegram: {error}")
            _safe_print("Повторная попытка отправки сообщения в Telegram без разметки")
            _safe_print(f"Лог в Telegram пропущен: {error}")
            try:
                bot = self._get_bot()
                return await bot.send_message(chat_id=chat_id, text=text, parse_mode=None)
            except Exception as error:
                _safe_print(f"Ошибка при отправке сообщения в Telegram без разметки: {error}")
                _safe_print(f"Сообщение: {text}")
        return None

    def log(self, text: str) -> None:
        func = self.send_message(self.default_chat_id, text)
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(func, loop)

    async def alog(self, text: str) -> Any:
        return await self.send_message(self.default_chat_id, text, parse_mode=None)


class AsyncOpenAIChatAgent:
    """Async OpenAI chat adapter used by reminder pipeline."""

    def __init__(
        self,
        api_key: str,
        proxies: Mapping[str, str] | None = None,
        model: str | None = None,
        organization: str | None = None,
        logger: LoggerAdapter | None = None,
        timeout_seconds: float = 25.0,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.8,
    ) -> None:

        self.api_key = api_key
        self.organization = organization
        self.proxies = dict(proxies or {})
        self.endpoint = 'https://api.openai.com/v1/chat/completions'
        self.model = model
        self.logger = logger or NullLogger()
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.retry_attempts = max(1, int(retry_attempts))
        self.retry_backoff_seconds = max(0.0, float(retry_backoff_seconds))
        proxy_url = _sanitize_proxy_url(self.proxies.get("https://") or self.proxies.get("http://"))
        client_kwargs = {"timeout": self.timeout_seconds}
        if proxy_url:
            # httpx>=0.28 uses singular "proxy" argument.
            client_kwargs["proxy"] = proxy_url
        self.http_client = httpx.AsyncClient(**client_kwargs)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            http_client=self.http_client,
        )


    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        """Call OpenAI chat completion with transient retry guard."""

        _safe_print(f"openai_proxies={self.proxies}")

        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        if not model:
            model = self.model
        if not model:
            model = "gpt-3.5-turbo"

        _safe_print(f"openai_messages={messages}")

        completion = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                break
            except Exception as error:
                transient = _is_transient_llm_error(error)
                can_retry = transient and attempt < self.retry_attempts
                if can_retry:
                    await asyncio.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))
                    continue
                self.logger.log(
                    "OpenAI chat error: "
                    f"attempt={attempt}/{self.retry_attempts} transient={transient} error={error}",
                )
                return None

        if completion is None:
            return None
        return completion.choices[0].message.content

    async def aclose(self) -> None:
        await self.http_client.aclose()


def _normalize_chat_messages(messages: Any) -> list[dict[str, str]]:
    """Return chat messages as normalized role/content dictionaries."""

    if isinstance(messages, str):
        return [{"role": "user", "content": messages}]
    if not isinstance(messages, list):
        return []

    normalized: list[dict[str, str]] = []
    for item in messages:
        if not isinstance(item, Mapping):
            continue
        role = str(item.get("role", "user"))
        content = str(item.get("content", ""))
        normalized.append({"role": role, "content": content})
    return normalized


def _extract_status_code(error: Exception) -> int | None:
    status_code = getattr(error, "status_code", None)
    if status_code is None:
        response = getattr(error, "response", None)
        if response is not None:
            status_code = getattr(response, "status_code", None)
    try:
        return int(status_code) if status_code is not None else None
    except (TypeError, ValueError):
        return None


def _is_transient_llm_error(error: Exception) -> bool:
    if isinstance(error, (asyncio.TimeoutError, TimeoutError, aiohttp.ClientError, httpx.TransportError)):
        return True
    status_code = _extract_status_code(error)
    if status_code in {408, 425, 429, 500, 502, 503, 504}:
        return True
    error_text = str(error).lower()
    return any(
        token in error_text
        for token in (
            "timeout",
            "timed out",
            "temporary",
            "temporarily",
            "rate limit",
            "too many requests",
            "bad gateway",
            "service unavailable",
            "gateway timeout",
        )
    )


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
        self.http_client = httpx.AsyncClient(timeout=self.timeout_seconds)

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        normalized = _normalize_chat_messages(messages)
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
                transient = _is_transient_llm_error(error)
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


class AsyncYandexLLMChatAgent:
    """Async YandexGPT adapter via Foundation Models completion API."""

    def __init__(
        self,
        api_key: str,
        model_uri: str,
        logger: LoggerAdapter | None = None,
        timeout_seconds: float = 25.0,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.8,
    ) -> None:
        self.api_key = str(api_key or "")
        self.model_uri = str(model_uri or "")
        self.logger = logger or NullLogger()
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.retry_attempts = max(1, int(retry_attempts))
        self.retry_backoff_seconds = max(0.0, float(retry_backoff_seconds))
        self.endpoint = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.http_client = httpx.AsyncClient(timeout=self.timeout_seconds)

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        normalized = _normalize_chat_messages(messages)
        if not normalized:
            return None

        model_uri = str(model or self.model_uri)
        request_messages = [
            {
                "role": str(item["role"]),
                "text": str(item["content"]),
            }
            for item in normalized
        ]
        request_body = {
            "modelUri": model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.2,
                "maxTokens": "3000",
            },
            "messages": request_messages,
        }
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = await self.http_client.post(self.endpoint, headers=headers, json=request_body)
                response.raise_for_status()
                payload = response.json()
                alternatives = ((payload.get("result") or {}).get("alternatives")) or []
                if not alternatives:
                    return None
                return str(((alternatives[0].get("message") or {}).get("text")) or "")
            except Exception as error:
                transient = _is_transient_llm_error(error)
                can_retry = transient and attempt < self.retry_attempts
                if can_retry:
                    await asyncio.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))
                    continue
                self.logger.log(
                    "Yandex LLM chat error: "
                    f"attempt={attempt}/{self.retry_attempts} transient={transient} error={error}",
                )
                return None
        return None

    async def aclose(self) -> None:
        await self.http_client.aclose()


class MockOpenAIChatAgent:
    """Mock агент для тестового режима без внешних вызовов OpenAI."""

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        if isinstance(messages, str):
            return messages
        if isinstance(messages, list):
            for message in reversed(messages):
                if message.get("role") == "user":
                    return message.get("content")
        return None


class Reminder:
    """Reminder orchestration for designer notifications."""

    def __init__(
        self,
        task_repository: Any,
        openai_agent: ChatAdapter,
        helper_character: str,
        tg_bot_token: str | None = None,
        people_manager: Any = None,
        mock_openai: bool = False,
        mock_telegram: bool = False,
        telegram_adapter: MessageAdapter | None = None,
        enhance_concurrency: int = 4,
        send_retry_attempts: int = 3,
        send_retry_backoff_seconds: float = 0.5,
        send_retry_backoff_multiplier: float = 2.0,
        sleep_func: Callable[[float], Any] | None = None,
        llm_provider_name: str = "openai",
    ) -> None:
        self.task_repository = task_repository
        self.openai_agent = openai_agent
        self.mock_openai = bool(mock_openai)
        self.mock_telegram = bool(mock_telegram)
        if self.mock_telegram:
            self.tg_bot = None
        else:
            self.tg_bot = telegram_adapter or TelegramNotifier(tg_bot_token)
        self.helper_character = helper_character
        self.llm_provider_name = str(llm_provider_name or "openai")
        self.draft_messages = {}
        self.enhanced_messages = {}
        self.sent_delivery_keys = set()
        self.today = None
        self.next_work_day = None
        self.people_manager = people_manager
        self.enhance_concurrency = max(1, int(enhance_concurrency))
        self.enhance_semaphore = asyncio.Semaphore(self.enhance_concurrency)
        self.send_retry_attempts = max(1, int(send_retry_attempts))
        self.send_retry_backoff_seconds = max(0.0, float(send_retry_backoff_seconds))
        self.send_retry_backoff_multiplier = max(1.0, float(send_retry_backoff_multiplier))
        self._sleep = sleep_func or asyncio.sleep
        self.delivery_counters = {}
        self.enhancement_counters = {}
        self.reset_delivery_counters()
        self.reset_enhancement_counters()

    def reset_delivery_counters(self) -> None:
        self.delivery_counters = {
            "candidates_total": 0,
            "sent": 0,
            "skipped_no_message": 0,
            "skipped_no_person": 0,
            "skipped_no_chat_id": 0,
            "skipped_vacation": 0,
            "skipped_mock": 0,
            "skipped_duplicate": 0,
            "send_errors": 0,
            "send_retry_attempts": 0,
            "send_retry_exhausted": 0,
            "send_error_transient": 0,
            "send_error_permanent": 0,
            "send_error_unknown": 0,
        }

    def _inc_delivery_counter(self, key: str, value: int = 1) -> None:
        self.delivery_counters[key] = int(self.delivery_counters.get(key, 0)) + int(value)

    def get_delivery_counters(self) -> dict[str, int]:
        return dict(self.delivery_counters)

    def reset_enhancement_counters(self) -> None:
        self.enhancement_counters = {
            "provider": self.llm_provider_name,
            "candidates_total": 0,
            "attempted": 0,
            "succeeded": 0,
            "fallback_empty": 0,
            "fallback_exception": 0,
            "skipped_mock": 0,
        }

    def _inc_enhancement_counter(self, key: str, value: int = 1) -> None:
        if key == "provider":
            return
        self.enhancement_counters[key] = int(self.enhancement_counters.get(key, 0)) + int(value)

    def get_enhancement_counters(self) -> dict[str, Any]:
        return dict(self.enhancement_counters)

    def _build_reminder_context(self) -> tuple[pd.Timestamp, pd.Timestamp, dict[str, list[Any]], dict[str, list[Any]]]:
        today, next_work_day = self.calculate_dates()
        tasks_today = self.distribute_tasks(today)
        tasks_next_day = self.distribute_tasks(next_work_day)
        return today, next_work_day, tasks_today, tasks_next_day

    @staticmethod
    def _collect_designers(
        tasks_today: Mapping[str, list[Any]],
        tasks_next_day: Mapping[str, list[Any]],
    ) -> list[str]:
        return sorted(set(tasks_today.keys()) | set(tasks_next_day.keys()))

    async def get_tasks_for_date(self, date: pd.Timestamp) -> list[Any]:
        return self.task_repository.get_tasks_by_date(date)

    async def _build_designer_message(
        self,
        designer: str,
        tasks_today: Mapping[str, list[Any]],
        tasks_next_day: Mapping[str, list[Any]],
    ) -> str | None:
        return await self.get_enhanced_message(
            designer,
            tasks_today.get(designer, []),
            tasks_next_day.get(designer, []),
        )

    async def _enhance_message_limited(self, message: str) -> str | None:
        async with self.enhance_semaphore:
            return await self.enhance_message(message)

    async def get_enhanced_message(
        self,
        designer: str,
        tasks_today: list[Any],
        tasks_next_day: list[Any],
    ) -> str | None:
        draft = self.generate_draft_message(designer, tasks_today, tasks_next_day)
        if draft:
            self.draft_messages[designer] = draft  # Сохраняем черновое сообщение
            if self.mock_openai:
                self.enhanced_messages[designer] = draft
                self._inc_enhancement_counter("skipped_mock")
                return draft
            self._inc_enhancement_counter("attempted")
            try:
                enhanced = await self._enhance_message_limited(draft)
                if not enhanced:
                    _safe_print("chat_enhancer_empty_response: fallback_to_draft")
                    enhanced = draft
                    self._inc_enhancement_counter("fallback_empty")
                else:
                    self._inc_enhancement_counter("succeeded")
                self.enhanced_messages[designer] = enhanced  # Сохраняем улучшенное сообщение
                return enhanced
            except Exception as e:
                # В случае ошибки при обращении к серверу, вернуть исходное сообщение
                _safe_print(f"chat_enhancer_error: {e}")
                self._inc_enhancement_counter("fallback_exception")
                self.enhanced_messages[designer] = draft
                return draft

        return None

    def calculate_dates(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        self.today = pd.Timestamp.today().normalize()
        dow = self.today.dayofweek
        day = pd.Timedelta(days=1)
        self.next_work_day = self.today + day * (7-dow) if dow in {4, 5} else self.today + day
        return self.today, self.next_work_day

    def distribute_tasks(self, date: pd.Timestamp) -> dict[str, list[Any]]:
        tasks = self.task_repository.get_tasks_by_date(date)
        tasks_by_designer = defaultdict(list)
        for task in tasks:
            tasks_by_designer[task.designer].append(task)
        return tasks_by_designer

    def day_messages(self, tasks: Iterable[Any], day: pd.Timestamp) -> list[str]:
        """Build lines for one day section in reminder draft."""
        day_lines: list[str] = []
        idx = 1
        for task in tasks:
            format_ = task.format_.split('\n')[0]
            stages = filter_stages(task.timing[day])
            if stages:
                stages = ', '.join(stages)
                day_lines.append(
                    f'{idx}. {task.brand} // {format_} // для проекта «{task.project_name}» - сдаём «{stages}»',
                )
                idx += 1
        return day_lines

    def generate_draft_message(
        self,
        designer: str,
        tasks_today: list[Any],
        tasks_next_day: list[Any],
    ) -> str | None:
        """Сформировать черновое сообщение для дизайнера.

        Args:
            designer (str): Имя дизайнера.
            tasks_today (list): Список задач на сегодня.
            tasks_next_day (list): Список задач на завтра.

        Returns:
            str: Черновое сообщение.
        """
        moscow_tz = pytz.timezone('Europe/Moscow')
        now_moscow = pd.Timestamp.now(tz=moscow_tz)
        today_str = now_moscow.strftime('%A, %d.%m')
        time_str = now_moscow.strftime('%H:%M')
        intro = f'Привет {designer}! Сегодня {today_str} в {time_str}.\n'
        m = intro

        today_messages = self.day_messages(tasks_today, self.today)
        if today_messages:
            tasks = '\n'.join(today_messages)
            m += f'\nЗадачи на сегодня:\n{tasks})'
        next_day_messages = self.day_messages(tasks_next_day, self.next_work_day)
        if next_day_messages:
            next_day_str = self.next_work_day.strftime('%A, %d.%m')
            tasks = '\n'.join(next_day_messages)
            m += f'\nЗадачи на {next_day_str}:\n{tasks})'

        return None if m == intro else m

    async def enhance_message(self, message: str) -> str | None:
        """Улучшение сообщения с помощью GPT.

        Args:
            message (str): Сообщение.

        Returns:
            str: Улучшенное сообщение.
        """
        instruction = {
            'role': 'system',
            'content': self.helper_character,
        }
        user_input = {'role': 'user', 'content': message}
        return await self.openai_agent.chat(messages=[instruction, user_input])

    async def get_reminders(self) -> dict[str, str | None]:
        """Получить напоминания.

        Returns:
            dict: Словарь улучшенных сообщений.
        """
        self.reset_enhancement_counters()
        _, _, tasks_today, tasks_next_day = self._build_reminder_context()
        designers = self._collect_designers(tasks_today, tasks_next_day)
        self._inc_enhancement_counter("candidates_total", len(designers))
        tasks = [
            self._build_designer_message(designer, tasks_today, tasks_next_day)
            for designer in designers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for designer, result in zip(designers, results):
            if isinstance(result, Exception):
                _safe_print(f"chat_enhancer_unhandled_error: {designer=} {result}")

        return self.enhanced_messages

    def _resolve_delivery_message(self, designer_name: str, message: str | None) -> str | None:
        if message:
            return message

        fallback_message = self.draft_messages.get(designer_name)
        if fallback_message:
            self.enhanced_messages[designer_name] = fallback_message
            _safe_print(f"empty_message_fallback: using draft for {designer_name}")
            return fallback_message

        _safe_print(f"empty_message_skip: no draft for {designer_name}")
        self._inc_delivery_counter("skipped_no_message")
        return None

    def _resolve_delivery_target(self, designer_name: str, mode: str) -> tuple[Any, Any, bool]:
        designer = self.people_manager.get_person(designer_name)
        if not designer:
            self._inc_delivery_counter("skipped_no_person")
            return None, None, False
        test_chat_id = 91864013
        test = mode == 'test'
        chat_id = test_chat_id if test else designer.chat_id
        if not chat_id:
            self._inc_delivery_counter("skipped_no_chat_id")
            return designer, chat_id, False
        if designer.vacation == '\u0434\u0430':
            self._inc_delivery_counter("skipped_vacation")
            return designer, chat_id, False
        can_send = bool(self.tg_bot)
        return designer, chat_id, can_send

    async def _deliver_message(self, designer_name: str, chat_id: Any, message: str) -> None:
        delivery_key = self._build_delivery_key(designer_name, chat_id, message)
        if delivery_key in self.sent_delivery_keys:
            _safe_print(f"duplicate_reminder_skip: {designer_name} chat_id={chat_id}")
            self._inc_delivery_counter("skipped_duplicate")
            return
        for attempt in range(1, self.send_retry_attempts + 1):
            try:
                await self.tg_bot.send_message(chat_id, message)
                self.sent_delivery_keys.add(delivery_key)
                self._inc_delivery_counter("sent")
                return
            except Exception as e:
                classification = self._classify_send_error(e)
                transient = classification["is_transient"]
                error_kind = classification["kind"]
                can_retry = transient and attempt < self.send_retry_attempts
                if can_retry:
                    self._inc_delivery_counter("send_retry_attempts")
                    delay = self._get_retry_backoff_delay(attempt)
                    _safe_print(
                        "reminder_send_retry: "
                        f"{designer_name} chat_id={chat_id} attempt={attempt + 1}/{self.send_retry_attempts} "
                        f"delay_seconds={delay} error_kind={error_kind} error={e}"
                    )
                    await self._sleep(delay)
                    continue

                if transient and attempt > 1:
                    self._inc_delivery_counter("send_retry_exhausted")
                _safe_print(
                    "reminder_send_error: "
                    f"{designer_name} chat_id={chat_id} attempt={attempt}/{self.send_retry_attempts} "
                    f"transient={transient} error_kind={error_kind} error={e}"
                )
                self._track_send_error_kind(classification)
                self._inc_delivery_counter("send_errors")
                return

    def _get_retry_backoff_delay(self, failed_attempt: int) -> float:
        return self.send_retry_backoff_seconds * (self.send_retry_backoff_multiplier ** (failed_attempt - 1))

    @staticmethod
    def _classify_send_error(error: Exception) -> dict[str, Any]:
        if isinstance(error, (asyncio.TimeoutError, TimeoutError, aiohttp.ClientError, httpx.TransportError)):
            return {"is_transient": True, "kind": "timeout_or_transport"}
        error_name = type(error).__name__
        if error_name in {"TimedOut", "NetworkError"}:
            return {"is_transient": True, "kind": "network_error_name"}
        if error_name == "RetryAfter":
            return {"is_transient": True, "kind": "rate_limit_name"}

        retry_after = getattr(error, "retry_after", None)
        if retry_after is not None:
            return {"is_transient": True, "kind": "rate_limit_attr"}

        status_code = getattr(error, "status_code", None)
        response = getattr(error, "response", None)
        if status_code is None and response is not None:
            status_code = getattr(response, "status_code", None)

        if status_code in {408, 425, 429, 500, 502, 503, 504}:
            return {"is_transient": True, "kind": f"http_{status_code}"}
        if status_code in {400, 401, 403, 404}:
            return {"is_transient": False, "kind": f"http_{status_code}"}

        error_text = str(error).lower()
        transient_markers = (
            "timeout",
            "timed out",
            "temporary",
            "temporarily",
            "rate limit",
            "too many requests",
            "connection reset",
            "connection aborted",
            "connection refused",
            "bad gateway",
            "service unavailable",
            "gateway timeout",
        )
        if any(marker in error_text for marker in transient_markers):
            return {"is_transient": True, "kind": "message_transient"}

        permanent_markers = (
            "chat not found",
            "bot was blocked",
            "forbidden",
            "bad request",
            "can't parse entities",
            "message is too long",
        )
        if any(marker in error_text for marker in permanent_markers):
            return {"is_transient": False, "kind": "message_permanent"}

        return {"is_transient": False, "kind": "unknown"}

    def _track_send_error_kind(self, classification: Mapping[str, Any]) -> None:
        if classification["is_transient"]:
            self._inc_delivery_counter("send_error_transient")
            return
        if classification["kind"] == "unknown":
            self._inc_delivery_counter("send_error_unknown")
            return
        self._inc_delivery_counter("send_error_permanent")

    async def send_reminders(self, mode: str = 'test') -> None:
        """Отправить напоминания.

        Args:
            mode (str): Режим работы.
        """
        self.reset_delivery_counters()
        self._inc_delivery_counter("candidates_total", len(self.enhanced_messages))

        for designer_name, message in self.enhanced_messages.items():
            resolved_message = self._resolve_delivery_message(designer_name, message)
            if not resolved_message:
                continue

            if self.mock_telegram:
                _safe_print(f'mock_telegram_send: skipped for {designer_name} to chat_id=None')
                self._inc_delivery_counter("skipped_mock")
                continue
            _, chat_id, can_send = self._resolve_delivery_target(designer_name, mode)
            _safe_print(f'{mode=} {designer_name=} {chat_id=} {resolved_message=}')
            if can_send:
                await self._deliver_message(designer_name, chat_id, resolved_message)
        _safe_print(f"reminder_delivery_counters={json.dumps(self.delivery_counters, ensure_ascii=False, sort_keys=True)}")

    def _build_delivery_key(self, designer_name: str, chat_id: Any, message: str) -> str:
        normalized_day = (
            str(self.today.date())
            if isinstance(self.today, pd.Timestamp)
            else str(pd.Timestamp.today().date())
        )
        msg_hash = hashlib.sha256(str(message).encode("utf-8")).hexdigest()[:16]
        return f"{normalized_day}|{designer_name}|{chat_id}|{msg_hash}"



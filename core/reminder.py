"""Reminder pipeline: draft generation, enhancement, and Telegram delivery."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

import pandas as pd
import pytz

from core.adapters import ChatAdapter, LoggerAdapter, MessageAdapter, NullLogger
from core.reminder_policy import classify_delivery_error
from core.task_query_adapter import build_task_query_context, query_projections
from core.task_query_contract import TimeWindow, milestones_in_window
from src.adapters.llm_google import AsyncGoogleLLMChatAgent
from src.adapters.llm_openai import AsyncOpenAIChatAgent
from src.adapters.llm_yandex import AsyncYandexLLMChatAgent
from src.adapters.telegram import TelegramNotifier
from utils.func import filter_stages


def _safe_print(text: Any) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("unicode_escape").decode("ascii"))


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


class FallbackChatAdapter:
    """Chat adapter wrapper supporting optional provider failover."""

    def __init__(
        self,
        primary: ChatAdapter,
        primary_provider: str,
        mode: str = "draft_only",
        fallback: ChatAdapter | None = None,
        fallback_provider: str = "",
    ) -> None:
        self.primary = primary
        self.primary_provider = str(primary_provider or "openai")
        self.mode = str(mode or "draft_only")
        self.fallback = fallback
        self.fallback_provider = str(fallback_provider or "")
        self.counters: dict[str, Any] = {}
        self.reset_counters()

    def reset_counters(self) -> None:
        self.counters = {
            "mode": self.mode,
            "primary_provider": self.primary_provider,
            "fallback_provider": self.fallback_provider,
            "primary_calls": 0,
            "primary_errors": 0,
            "fallback_calls": 0,
            "fallback_success": 0,
            "fallback_failure": 0,
            "fallback_skipped": 0,
        }

    def get_failover_counters(self) -> dict[str, Any]:
        return dict(self.counters)

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        self.counters["primary_calls"] = int(self.counters.get("primary_calls", 0)) + 1
        primary_result: str | None = None
        try:
            primary_result = await self.primary.chat(messages=messages, model=model)
        except Exception:
            self.counters["primary_errors"] = int(self.counters.get("primary_errors", 0)) + 1
            primary_result = None

        if primary_result:
            return primary_result

        if self.mode != "provider" or not self.fallback:
            self.counters["fallback_skipped"] = int(self.counters.get("fallback_skipped", 0)) + 1
            return None

        self.counters["fallback_calls"] = int(self.counters.get("fallback_calls", 0)) + 1
        try:
            fallback_result = await self.fallback.chat(messages=messages, model=model)
        except Exception:
            fallback_result = None
        if fallback_result:
            self.counters["fallback_success"] = int(self.counters.get("fallback_success", 0)) + 1
            return fallback_result
        self.counters["fallback_failure"] = int(self.counters.get("fallback_failure", 0)) + 1
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
        counters = dict(self.enhancement_counters)
        failover_getter = getattr(self.openai_agent, "get_failover_counters", None)
        if callable(failover_getter):
            failover = failover_getter()
            for key, value in dict(failover).items():
                counters[f"failover_{key}"] = value
        return counters

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

    def _get_tasks_for_date_sync(self, date: pd.Timestamp) -> list[Any]:
        tasks = self.task_repository.get_all_tasks()
        query_context = build_task_query_context(tasks)
        window = TimeWindow(start=date.date(), end=date.date(), mode="intersects")
        filtered = query_projections(
            query_context,
            statuses=["work"],
            window=window,
            limit=10**9,
        )
        return [
            item.source_task
            for item in filtered
            if item.source_task is not None and milestones_in_window(item, window)
        ]

    async def get_tasks_for_date(self, date: pd.Timestamp) -> list[Any]:
        return self._get_tasks_for_date_sync(date)

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
        tasks = self._get_tasks_for_date_sync(date)
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
        return classify_delivery_error(error)

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

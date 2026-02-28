"""Local smoke for reminder retry/backoff behavior on send failures."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Sequence

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.reminder import Reminder


class EchoChatAgent:
    async def chat(self, messages: Any, model: str | None = None) -> str:
        if isinstance(messages, list):
            return str(messages[-1].get("content"))
        return str(messages)


class FakeTaskRepository:
    def get_tasks_by_date(self, date: Any) -> list[Any]:
        return []


class FakePeopleManager:
    def get_person(self, designer_name: str) -> Any:
        if designer_name != "Alice":
            return None
        return SimpleNamespace(chat_id=1001, vacation="нет")


class SequencedTelegramAdapter:
    """Telegram adapter that replays a deterministic outcomes sequence."""

    def __init__(self, outcomes: Sequence[Any]) -> None:
        self.outcomes = list(outcomes)
        self.call_count = 0
        self.sent: list[tuple[Any, str]] = []

    async def send_message(
        self,
        chat_id: Any,
        text: str,
        parse_mode: str | None = "Markdown",
    ) -> Any:
        self.call_count += 1
        _ = parse_mode
        outcome = self.outcomes.pop(0) if self.outcomes else {"ok": True}
        if isinstance(outcome, Exception):
            raise outcome
        self.sent.append((chat_id, text))
        return outcome


async def noop_sleep(seconds: float) -> None:
    _ = seconds
    return None


class RetryAfter(Exception):
    def __init__(self, message: str, retry_after: int = 1) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class BadRequest(Exception):
    pass


def build_reminder(outcomes: Sequence[Any]) -> tuple[Reminder, SequencedTelegramAdapter]:
    """Build reminder with deterministic fake dependencies for retry smoke cases."""
    tg = SequencedTelegramAdapter(outcomes=outcomes)
    reminder = Reminder(
        task_repository=FakeTaskRepository(),
        openai_agent=EchoChatAgent(),
        helper_character="helper",
        tg_bot_token="dummy",
        people_manager=FakePeopleManager(),
        telegram_adapter=tg,
        send_retry_attempts=3,
        send_retry_backoff_seconds=0,
        sleep_func=noop_sleep,
    )
    reminder.enhanced_messages = {"Alice": "hello"}
    return reminder, tg


async def run_transient_success_case() -> None:
    reminder, tg = build_reminder(
        outcomes=[asyncio.TimeoutError("t1"), asyncio.TimeoutError("t2"), {"ok": True}]
    )
    await reminder.send_reminders(mode="morning")
    counters = reminder.get_delivery_counters()

    assert tg.call_count == 3, tg.call_count
    assert counters["sent"] == 1, counters
    assert counters["send_errors"] == 0, counters
    assert counters["send_retry_attempts"] == 2, counters
    assert counters["send_retry_exhausted"] == 0, counters
    assert counters["send_error_transient"] == 0, counters
    assert counters["send_error_permanent"] == 0, counters
    assert counters["send_error_unknown"] == 0, counters


async def run_transient_exhausted_case() -> None:
    reminder, tg = build_reminder(
        outcomes=[RetryAfter("rate limit"), RetryAfter("rate limit"), RetryAfter("rate limit")]
    )
    await reminder.send_reminders(mode="morning")
    counters = reminder.get_delivery_counters()

    assert tg.call_count == 3, tg.call_count
    assert counters["sent"] == 0, counters
    assert counters["send_errors"] == 1, counters
    assert counters["send_retry_attempts"] == 2, counters
    assert counters["send_retry_exhausted"] == 1, counters
    assert counters["send_error_transient"] == 1, counters
    assert counters["send_error_permanent"] == 0, counters
    assert counters["send_error_unknown"] == 0, counters


async def run_permanent_case() -> None:
    reminder, tg = build_reminder(outcomes=[BadRequest("chat not found"), {"ok": True}])
    await reminder.send_reminders(mode="morning")
    counters = reminder.get_delivery_counters()

    assert tg.call_count == 1, tg.call_count
    assert counters["sent"] == 0, counters
    assert counters["send_errors"] == 1, counters
    assert counters["send_retry_attempts"] == 0, counters
    assert counters["send_retry_exhausted"] == 0, counters
    assert counters["send_error_transient"] == 0, counters
    assert counters["send_error_permanent"] == 1, counters
    assert counters["send_error_unknown"] == 0, counters


async def run_unknown_case() -> None:
    reminder, tg = build_reminder(outcomes=[RuntimeError("boom"), {"ok": True}])
    await reminder.send_reminders(mode="morning")
    counters = reminder.get_delivery_counters()

    assert tg.call_count == 1, tg.call_count
    assert counters["sent"] == 0, counters
    assert counters["send_errors"] == 1, counters
    assert counters["send_retry_attempts"] == 0, counters
    assert counters["send_retry_exhausted"] == 0, counters
    assert counters["send_error_transient"] == 0, counters
    assert counters["send_error_permanent"] == 0, counters
    assert counters["send_error_unknown"] == 1, counters


async def run() -> None:
    await run_transient_success_case()
    await run_transient_exhausted_case()
    await run_permanent_case()
    await run_unknown_case()
    print("reminder_retry_backoff_smoke_ok")


if __name__ == "__main__":
    asyncio.run(run())

"""Local smoke for reminder retry/backoff behavior on transient send failures."""

from pathlib import Path
import sys
from types import SimpleNamespace
import asyncio

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.reminder import Reminder


class EchoChatAgent:
    async def chat(self, messages, model=None):
        if isinstance(messages, list):
            return messages[-1].get("content")
        return str(messages)


class FakeTaskRepository:
    def get_tasks_by_date(self, date):
        return []


class FakePeopleManager:
    def get_person(self, designer_name):
        if designer_name != "Alice":
            return None
        return SimpleNamespace(chat_id=1001, vacation="нет")


class SequencedTelegramAdapter:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.call_count = 0
        self.sent = []

    async def send_message(self, chat_id, text, parse_mode="Markdown"):
        self.call_count += 1
        outcome = self.outcomes.pop(0) if self.outcomes else {"ok": True}
        if isinstance(outcome, Exception):
            raise outcome
        self.sent.append((chat_id, text))
        return outcome


async def noop_sleep(seconds):
    return None


class RetryAfter(Exception):
    def __init__(self, message, retry_after=1):
        super().__init__(message)
        self.retry_after = retry_after


class BadRequest(Exception):
    pass


async def run_transient_success_case():
    tg = SequencedTelegramAdapter(
        outcomes=[asyncio.TimeoutError("t1"), asyncio.TimeoutError("t2"), {"ok": True}]
    )
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


async def run_transient_exhausted_case():
    tg = SequencedTelegramAdapter(
        outcomes=[RetryAfter("rate limit"), RetryAfter("rate limit"), RetryAfter("rate limit")]
    )
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


async def run_permanent_case():
    tg = SequencedTelegramAdapter(outcomes=[BadRequest("chat not found"), {"ok": True}])
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


async def run_unknown_case():
    tg = SequencedTelegramAdapter(outcomes=[RuntimeError("boom"), {"ok": True}])
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


async def run():
    await run_transient_success_case()
    await run_transient_exhausted_case()
    await run_permanent_case()
    await run_unknown_case()
    print("reminder_retry_backoff_smoke_ok")


if __name__ == "__main__":
    asyncio.run(run())

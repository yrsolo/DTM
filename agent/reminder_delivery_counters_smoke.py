"""Local smoke for reminder delivery outcome counters."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

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
        _ = date
        return []


class FakePeopleManager:
    def get_person(self, designer_name: str) -> Any:
        mapping = {
            "Alice": SimpleNamespace(chat_id=1001, vacation="нет"),
            "NoChat": SimpleNamespace(chat_id="", vacation="нет"),
            "Vacation": SimpleNamespace(chat_id=1003, vacation="да"),
        }
        return mapping.get(designer_name)


class FakeTelegramAdapter:
    def __init__(self) -> None:
        self.sent: list[tuple[Any, str]] = []

    async def send_message(
        self,
        chat_id: Any,
        text: str,
        parse_mode: str | None = "Markdown",
    ) -> dict[str, bool]:
        _ = parse_mode
        self.sent.append((chat_id, text))
        return {"ok": True}


async def run() -> None:
    tg = FakeTelegramAdapter()
    reminder = Reminder(
        task_repository=FakeTaskRepository(),
        openai_agent=EchoChatAgent(),
        helper_character="helper",
        tg_bot_token="dummy",
        people_manager=FakePeopleManager(),
        mock_openai=False,
        mock_telegram=False,
        telegram_adapter=tg,
    )

    reminder.enhanced_messages = {
        "Alice": "msg-1",
        "MissingPerson": "msg-2",
        "NoChat": "msg-3",
        "Vacation": "msg-4",
        "NoMsg": "",
    }
    reminder.draft_messages = {"NoMsg": None}

    await reminder.send_reminders(mode="morning")
    counters = reminder.get_delivery_counters()

    assert counters["candidates_total"] == 5, counters
    assert counters["sent"] == 1, counters
    assert counters["skipped_no_person"] == 1, counters
    assert counters["skipped_no_chat_id"] == 1, counters
    assert counters["skipped_vacation"] == 1, counters
    assert counters["skipped_no_message"] == 1, counters
    assert counters["send_errors"] == 0, counters
    assert counters["skipped_duplicate"] == 0, counters
    assert counters["skipped_mock"] == 0, counters
    assert len(tg.sent) == 1, tg.sent
    print("reminder_delivery_counters_smoke_ok")


if __name__ == "__main__":
    asyncio.run(run())

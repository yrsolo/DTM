"""Local smoke for reminder fallback when enhancer returns empty response."""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.reminder import Reminder

DESIGN_STEP = "\u0434\u0438\u0437\u0430\u0439\u043d"
NO_VACATION = "\u043d\u0435\u0442"


class EmptyChatAgent:
    """Stub enhancer that always returns empty output to trigger fallback."""

    async def chat(self, messages: Any, model: str | None = None) -> None:
        _ = messages
        _ = model
        return None


class FakeTaskRepository:
    """Single-task repository stub for fallback scenario."""

    def get_tasks_by_date(self, date: str) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                designer="Alice",
                brand="BrandX",
                format_="Post\nlong",
                project_name="ProjectX",
                timing={date: [DESIGN_STEP]},
            )
        ]


class FakePeopleManager:
    """People manager stub with non-vacation user."""

    def get_person(self, designer_name: str) -> SimpleNamespace:
        _ = designer_name
        return SimpleNamespace(chat_id=123456, vacation=NO_VACATION)


async def run() -> None:
    """Validate fallback to draft reminder when enhancement returns empty text."""
    reminder = Reminder(
        task_repository=FakeTaskRepository(),
        openai_agent=EmptyChatAgent(),
        helper_character="helper",
        tg_bot_token="dummy",
        people_manager=FakePeopleManager(),
        mock_openai=False,
        mock_telegram=True,
        telegram_adapter=None,
    )

    enhanced_messages = await reminder.get_reminders()
    assert "Alice" in enhanced_messages
    assert enhanced_messages["Alice"] is not None
    assert enhanced_messages["Alice"] == reminder.draft_messages["Alice"]

    await reminder.send_reminders(mode="test")
    print("reminder_fallback_smoke_ok")


if __name__ == "__main__":
    asyncio.run(run())

"""Local smoke for reminder fallback when enhancer returns empty response."""

from pathlib import Path
import sys
from types import SimpleNamespace

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.reminder import Reminder


class EmptyChatAgent:
    async def chat(self, messages, model=None):
        return None


class FakeTaskRepository:
    def get_tasks_by_date(self, date):
        return [
            SimpleNamespace(
                designer="Alice",
                brand="BrandX",
                format_="Post\nlong",
                project_name="ProjectX",
                timing={date: ["дизайн"]},
            )
        ]


class FakePeopleManager:
    def get_person(self, designer_name):
        return SimpleNamespace(chat_id=123456, vacation="нет")


async def run():
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
    import asyncio

    asyncio.run(run())

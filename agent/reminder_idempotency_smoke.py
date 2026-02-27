"""Local smoke for in-run idempotent reminder delivery guard."""

from pathlib import Path
import sys
from types import SimpleNamespace

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
        return [
            SimpleNamespace(
                designer="Alice",
                brand="BrandX",
                format_="Post",
                project_name="ProjectX",
                timing={date: ["дизайн"]},
            )
        ]


class FakePeopleManager:
    def get_person(self, designer_name):
        return SimpleNamespace(chat_id=555001, vacation="нет")


class FakeTelegramAdapter:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, parse_mode="Markdown"):
        self.sent.append((chat_id, text))
        return {"ok": True}


async def run():
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

    await reminder.get_reminders()
    await reminder.send_reminders(mode="morning")
    await reminder.send_reminders(mode="morning")

    assert len(tg.sent) == 1, f"expected single send, got {len(tg.sent)}"
    print("reminder_idempotency_smoke_ok")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())

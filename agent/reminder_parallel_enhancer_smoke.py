"""Local smoke for parallel reminder enhancement fan-out."""

from pathlib import Path
import sys
from types import SimpleNamespace
import asyncio

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.reminder import Reminder


class ParallelProbeChatAgent:
    def __init__(self):
        self.active = 0
        self.max_active = 0

    async def chat(self, messages, model=None):
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(0.05)
            if isinstance(messages, list):
                return messages[-1].get("content")
            return str(messages)
        finally:
            self.active -= 1


class FakeTaskRepository:
    def get_tasks_by_date(self, date):
        return [
            SimpleNamespace(
                designer="Alice",
                brand="BrandX",
                format_="Post",
                project_name="ProjectX",
                timing={date: ["Ð´Ð¸Ð·Ð°Ð¹Ð½"]},
            ),
            SimpleNamespace(
                designer="Bob",
                brand="BrandY",
                format_="Story",
                project_name="ProjectY",
                timing={date: ["Ð´Ð¸Ð·Ð°Ð¹Ð½"]},
            ),
        ]


class FakePeopleManager:
    def get_person(self, designer_name):
        return SimpleNamespace(chat_id=555001, vacation="Ð½ÐµÑ‚")


async def run():
    probe_agent = ParallelProbeChatAgent()
    reminder = Reminder(
        task_repository=FakeTaskRepository(),
        openai_agent=probe_agent,
        helper_character="helper",
        tg_bot_token="dummy",
        people_manager=FakePeopleManager(),
        mock_openai=False,
        mock_telegram=True,
        telegram_adapter=None,
        enhance_concurrency=4,
    )

    enhanced_messages = await reminder.get_reminders()
    assert len(enhanced_messages) == 2, f"expected 2 messages, got {len(enhanced_messages)}"
    assert probe_agent.max_active >= 2, f"expected parallel fan-out, got max_active={probe_agent.max_active}"
    print(f"reminder_parallel_enhancer_smoke_ok max_active={probe_agent.max_active}")


if __name__ == "__main__":
    asyncio.run(run())

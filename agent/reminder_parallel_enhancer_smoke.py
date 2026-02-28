"""Local smoke for parallel reminder enhancement fan-out."""

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


class ParallelProbeChatAgent:
    """Probe concurrent OpenAI enhancement fan-out calls."""

    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    async def chat(self, messages: Any, model: str | None = None) -> str:
        _ = model
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(0.05)
            if isinstance(messages, list):
                return str(messages[-1].get("content", ""))
            return str(messages)
        finally:
            self.active -= 1


class FakeTaskRepository:
    """Minimal repository stub for two reminder candidates on one date."""

    def get_tasks_by_date(self, date: str) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                designer="Alice",
                brand="BrandX",
                format_="Post",
                project_name="ProjectX",
                timing={date: [DESIGN_STEP]},
            ),
            SimpleNamespace(
                designer="Bob",
                brand="BrandY",
                format_="Story",
                project_name="ProjectY",
                timing={date: [DESIGN_STEP]},
            ),
        ]


class FakePeopleManager:
    """Minimal people manager stub used by reminder flow."""

    def get_person(self, designer_name: str) -> SimpleNamespace:
        _ = designer_name
        return SimpleNamespace(chat_id=555001, vacation=NO_VACATION)


async def run() -> None:
    """Execute fan-out smoke and assert concurrent enhancement calls happen."""
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

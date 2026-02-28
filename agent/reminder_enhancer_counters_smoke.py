"""Smoke check for reminder enhancer counters and fallback metrics."""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.planner import GoogleSheetPlanner
from core.reminder import Reminder

DESIGN_STEP = "дизайн"
NO_VACATION = "нет"


class EmptyChatAgent:
    async def chat(self, messages: Any, model: str | None = None) -> None:
        _ = messages
        _ = model
        return None


class FakeTaskRepository:
    def get_tasks_by_date(self, date: str) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                designer="Alice",
                brand="BrandX",
                format_="Post",
                project_name="ProjectX",
                timing={date: [DESIGN_STEP]},
            )
        ]


class FakePeopleManager:
    def get_person(self, designer_name: str) -> SimpleNamespace:
        _ = designer_name
        return SimpleNamespace(chat_id=123456, vacation=NO_VACATION)


async def run() -> None:
    reminder = Reminder(
        task_repository=FakeTaskRepository(),
        openai_agent=EmptyChatAgent(),
        helper_character="helper",
        tg_bot_token="dummy",
        people_manager=FakePeopleManager(),
        mock_openai=False,
        mock_telegram=True,
        llm_provider_name="google",
    )
    await reminder.get_reminders()
    counters = reminder.get_enhancement_counters()
    assert counters["provider"] == "google", counters
    assert counters["candidates_total"] == 1, counters
    assert counters["attempted"] == 1, counters
    assert counters["fallback_empty"] == 1, counters

    planner = GoogleSheetPlanner.__new__(GoogleSheetPlanner)
    planner.mode = "test"
    planner.dry_run = True
    planner.task_repository = SimpleNamespace(row_issues=[], timing_parser=SimpleNamespace(parse_issues=[], total_parse_errors=0))
    planner.people_manager = SimpleNamespace(row_issues=[])
    planner.reminder = reminder
    report = GoogleSheetPlanner.build_quality_report(planner)
    summary = report["summary"]
    assert summary["reminder_enhancer_provider"] == "google", summary
    assert summary["reminder_enhancer_attempt_count"] == 1, summary
    assert summary["reminder_enhancer_fallback_empty_count"] == 1, summary
    print("reminder_enhancer_counters_smoke_ok")


if __name__ == "__main__":
    asyncio.run(run())

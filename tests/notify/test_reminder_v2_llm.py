from __future__ import annotations

import asyncio
import unittest
from datetime import date, datetime, timezone

from src.notify.formatter import ReminderFormatter
from src.notify.job import ReminderJob
from src.notify.model import ReminderRequest
from src.notify.usecase import ReminderUseCase
from src.snapshot_engine.model import (
    Milestone,
    PeopleSnapshot,
    PersonView,
    PrepIndexes,
    PrepSnapshot,
    TaskSheet,
    TaskView,
)


class _FakeSender:
    async def send_message(self, chat_id: str, text: str):  # noqa: ANN201
        return {"chat_id": chat_id, "text": text}


class _FakeEnhancer:
    def __init__(self, response: str | None, raise_error: bool = False) -> None:
        self.response = response
        self.raise_error = raise_error

    async def chat(self, messages, model=None):  # noqa: ANN001,ANN201,ARG002
        if self.raise_error:
            raise RuntimeError("llm_failed")
        return self.response


class _FakeEngine:
    def __init__(self, prep: PrepSnapshot, people: PeopleSnapshot):
        self._prep = prep
        self._people = people

    def get_prep_snapshot(self) -> PrepSnapshot:
        return self._prep

    def get_people_snapshot(self) -> PeopleSnapshot:
        return self._people


def _task(day: date) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id="1",
            title="title",
            owner_id="Дизайнер",
            group_id="Проект",
            brand="Бренд",
            format_="граф. ролик",
            customer="Клиент",
            raw_timing="",
            status="work",
            history="история",
            timing={day.isoformat(): ["финал"]},
            milestones=[Milestone(type="финал", planned=day)],
        ),
        extra=None,
    )


class ReminderLlmTestCase(unittest.TestCase):
    def _build_job(self, enhancer: object) -> ReminderJob:
        today = date(2026, 3, 7)
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task(today)},
            indexes=PrepIndexes(),
        )
        people = PeopleSnapshot(
            source_id="sheet:test:people",
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name={
                "дизайнер": PersonView(name="Дизайнер", chat_id="-1001", vacation="", position="designer")
            },
        )
        engine = _FakeEngine(prep, people)
        return ReminderJob(
            usecase=ReminderUseCase(engine),
            formatter=ReminderFormatter(),
            sender=_FakeSender(),
            enhancer=enhancer,
            people_lookup=engine,
            default_chat_id="-999",
            llm_mode="provider",
            runtime_env="dev",
        )

    def test_enhancer_success(self) -> None:
        result = asyncio.run(
            self._build_job(_FakeEnhancer("improved")).run(
                ReminderRequest(mode="reminder_v2", today_override=date(2026, 3, 7))
            )
        )
        self.assertEqual(result.enhancement_counters["attempted"], 1)
        self.assertEqual(result.enhancement_counters["succeeded"], 1)
        self.assertEqual(result.messages.get("Дизайнер"), "improved")

    def test_enhancer_empty_fallbacks_to_draft(self) -> None:
        result = asyncio.run(
            self._build_job(_FakeEnhancer("")).run(ReminderRequest(mode="reminder_v2", today_override=date(2026, 3, 7)))
        )
        self.assertEqual(result.enhancement_counters["fallback_empty"], 1)
        self.assertIn("Задачи на сегодня", result.messages.get("Дизайнер", ""))

    def test_enhancer_exception_fallbacks_to_draft(self) -> None:
        result = asyncio.run(
            self._build_job(_FakeEnhancer(None, raise_error=True)).run(
                ReminderRequest(mode="reminder_v2", today_override=date(2026, 3, 7))
            )
        )
        self.assertEqual(result.enhancement_counters["fallback_exception"], 1)
        self.assertIn("Задачи на сегодня", result.messages.get("Дизайнер", ""))


if __name__ == "__main__":
    unittest.main()

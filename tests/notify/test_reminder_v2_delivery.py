from __future__ import annotations

import asyncio
import unittest
from datetime import date, datetime, timezone

from src.contexts.reminders.internal import (
    ReminderFormatter,
    ReminderJob,
    ReminderRequest,
    ReminderUseCase,
)
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
    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.sent: list[tuple[str, str]] = []

    async def send_message(self, chat_id: str, text: str):  # noqa: ANN201
        if self.failures > 0:
            self.failures -= 1
            raise RuntimeError("timeout")
        self.sent.append((chat_id, text))
        return {"ok": True}


class _FakeEngine:
    def __init__(self, prep: PrepSnapshot, people: PeopleSnapshot):
        self._prep = prep
        self._people = people

    def get_prep_snapshot(self) -> PrepSnapshot:
        return self._prep

    def get_people_snapshot(self) -> PeopleSnapshot:
        return self._people


def _task(task_id: str, owner: str, day: date) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=f"title-{task_id}",
            owner_id=owner,
            group_id="p",
            brand="b",
            format_="f",
            customer="c",
            raw_timing="",
            status="work",
            history="h",
            timing={day.isoformat(): ["финал"]},
            milestones=[Milestone(type="финал", planned=day)],
        ),
        extra=None,
    )


class ReminderDeliveryTestCase(unittest.TestCase):
    def _build(self, sender: _FakeSender, people: dict[str, PersonView]) -> ReminderJob:
        today = date(2026, 3, 7)
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "1": _task("1", "Дизайнер 1", today),
                "2": _task("2", "Дизайнер 2", today),
            },
            indexes=PrepIndexes(),
        )
        people_snapshot = PeopleSnapshot(
            source_id="sheet:test:people",
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name=people,
        )
        engine = _FakeEngine(prep, people_snapshot)
        return ReminderJob(
            usecase=ReminderUseCase(engine),
            formatter=ReminderFormatter(),
            sender=sender,
            enhancer=None,
            people_lookup=engine,
            default_chat_id="-900",
            llm_mode="draft_only",
            runtime_env="dev",
        )

    def test_skips_vacation_and_missing_person(self) -> None:
        sender = _FakeSender()
        people = {
            "дизайнер 1": PersonView(name="Дизайнер 1", chat_id="-1001", vacation="да", position="designer"),
        }
        result = asyncio.run(
            self._build(sender, people).run(ReminderRequest(mode="reminder_v2", today_override=date(2026, 3, 7)))
        )
        self.assertEqual(result.delivery_counters["skipped_vacation"], 1)
        self.assertEqual(result.delivery_counters["skipped_no_person"], 1)
        self.assertEqual(result.delivery_counters["sent"], 0)

    def test_test_mode_forces_test_chat(self) -> None:
        sender = _FakeSender()
        people = {
            "дизайнер 1": PersonView(name="Дизайнер 1", chat_id="-1001", vacation="", position="designer"),
            "дизайнер 2": PersonView(name="Дизайнер 2", chat_id="-1002", vacation="", position="designer"),
        }
        result = asyncio.run(
            self._build(sender, people).run(
                ReminderRequest(mode="test", today_override=date(2026, 3, 7), force_test_chat=True, test_chat_id_override="-777")
            )
        )
        self.assertEqual(result.delivery_counters["sent"], 2)
        self.assertTrue(all(chat_id == "-777" for chat_id, _ in sender.sent))

    def test_retry_then_success(self) -> None:
        sender = _FakeSender(failures=1)
        people = {
            "дизайнер 1": PersonView(name="Дизайнер 1", chat_id="-1001", vacation="", position="designer"),
            "дизайнер 2": PersonView(name="Дизайнер 2", chat_id="-1002", vacation="", position="designer"),
        }
        result = asyncio.run(
            self._build(sender, people).run(ReminderRequest(mode="reminder_v2", today_override=date(2026, 3, 7)))
        )
        self.assertGreaterEqual(result.delivery_counters["send_retry_attempts"], 1)
        self.assertEqual(result.delivery_counters["sent"], 2)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from datetime import date, datetime, timezone

from src.notify.model import ReminderRequest
from src.notify.usecase import ReminderUseCase, next_workday
from src.snapshot_engine.model import Milestone, PrepIndexes, PrepSnapshot, TaskSheet, TaskView


class _FakeEngine:
    def __init__(self, prep: PrepSnapshot | None):
        self._prep = prep

    def get_prep_snapshot(self) -> PrepSnapshot | None:
        return self._prep


def _task(task_id: str, owner: str, status: str, milestone_day: date) -> TaskView:
    iso = milestone_day.isoformat()
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=f"title-{task_id}",
            owner_id=owner,
            group_id="project",
            brand="brand",
            format_="format",
            customer="customer",
            raw_timing="raw",
            status=status,
            history="history",
            timing={iso: ["этап"]},
            milestones=[Milestone(type="этап", planned=milestone_day)],
        ),
        extra=None,
    )


class ReminderSelectionTestCase(unittest.TestCase):
    def test_selects_today_and_next_workday_only(self) -> None:
        today = date(2026, 3, 6)  # friday
        monday = date(2026, 3, 9)
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "1": _task("1", "Дизайнер 1", "work", today),
                "2": _task("2", "Дизайнер 1", "pre_done", monday),
                "3": _task("3", "Дизайнер 2", "done", today),
            },
            indexes=PrepIndexes(),
        )
        groups, selected_today, selected_next = ReminderUseCase(_FakeEngine(prep)).select(
            ReminderRequest(mode="reminder_v2", today_override=today)
        )
        self.assertEqual(selected_today, today)
        self.assertEqual(selected_next, monday)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].owner_name, "Дизайнер 1")
        self.assertEqual(len(groups[0].tasks_today), 1)
        self.assertEqual(len(groups[0].tasks_next_workday), 1)

    def test_next_workday_weekend_rules(self) -> None:
        self.assertEqual(next_workday(date(2026, 3, 6)), date(2026, 3, 9))  # Fri -> Mon
        self.assertEqual(next_workday(date(2026, 3, 7)), date(2026, 3, 9))  # Sat -> Mon
        self.assertEqual(next_workday(date(2026, 3, 8)), date(2026, 3, 9))  # Sun -> Mon


if __name__ == "__main__":
    unittest.main()

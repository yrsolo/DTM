from __future__ import annotations

import unittest
from unittest.mock import patch

from src.entrypoints.jobs.source_switch_job import apply_task_source_switches


class _PlannerStub:
    def __init__(self) -> None:
        self.task_repository = "orig"
        self.task_manager = type("TaskManager", (), {"repository": "orig"})()
        self.calendar_manager = type("CalendarManager", (), {"repository": "orig"})()
        self.task_calendar_manager = type("TaskCalendarManager", (), {"repository": "orig"})()
        self.reminder = type("Reminder", (), {"task_repository": "orig"})()


class SourceSwitchJobTestCase(unittest.TestCase):
    @patch("src.entrypoints.jobs.source_switch_job.YdbOperationalTaskRepository")
    def test_applies_render_and_notify_ydb_switches(self, repo_cls) -> None:  # noqa: ANN001
        repo_instance = object()
        repo_cls.return_value = repo_instance
        planner = _PlannerStub()
        logs = []

        render_switched, notify_switched = apply_task_source_switches(
            planner=planner,
            mode="test",
            render_source="ydb",
            notify_source="ydb",
            ydb_endpoint="endpoint",
            ydb_database="database",
            ydb_sa_json_credentials=None,
            ydb_sa_key_file=None,
            log=logs.append,
        )

        self.assertTrue(render_switched)
        self.assertTrue(notify_switched)
        self.assertIs(planner.task_repository, repo_instance)
        self.assertIs(planner.task_manager.repository, repo_instance)
        self.assertIs(planner.calendar_manager.repository, repo_instance)
        self.assertIs(planner.task_calendar_manager.repository, repo_instance)
        self.assertIs(planner.reminder.task_repository, repo_instance)
        self.assertTrue(any("render_source_switch=applied source=ydb" in line for line in logs))
        self.assertTrue(any("notify_source_switch=applied source=ydb" in line for line in logs))

    @patch("src.entrypoints.jobs.source_switch_job.YdbOperationalTaskRepository")
    def test_no_switch_when_policy_does_not_require_ydb(self, repo_cls) -> None:  # noqa: ANN001
        planner = _PlannerStub()
        render_switched, notify_switched = apply_task_source_switches(
            planner=planner,
            mode="timer",
            render_source="legacy",
            notify_source="legacy",
            ydb_endpoint="endpoint",
            ydb_database="database",
            ydb_sa_json_credentials=None,
            ydb_sa_key_file=None,
            log=lambda _: None,
        )
        self.assertFalse(render_switched)
        self.assertFalse(notify_switched)
        repo_cls.assert_not_called()
        self.assertEqual(planner.task_repository, "orig")
        self.assertEqual(planner.reminder.task_repository, "orig")


if __name__ == "__main__":
    unittest.main()

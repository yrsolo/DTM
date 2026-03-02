"""Tests for runtime source switching to store-backed repository."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

import main


class MainSourceSwitchTestCase(unittest.TestCase):
    def test_apply_task_source_switches_rebinds_render_and_notify(self) -> None:
        original_render_source = main.RENDER_SOURCE
        original_notify_source = main.NOTIFY_SOURCE
        original_builder = main._build_ydb_task_repository
        try:
            repo_marker = object()
            main.RENDER_SOURCE = "ydb"
            main.NOTIFY_SOURCE = "ydb"
            main._build_ydb_task_repository = lambda: repo_marker

            planner = SimpleNamespace(
                task_repository=object(),
                task_manager=SimpleNamespace(repository=object()),
                calendar_manager=SimpleNamespace(repository=object()),
                task_calendar_manager=SimpleNamespace(repository=object()),
                reminder=SimpleNamespace(task_repository=object()),
            )

            render_switched, notify_switched = main._apply_task_source_switches(planner, "test")

            self.assertTrue(render_switched)
            self.assertTrue(notify_switched)
            self.assertIs(planner.task_repository, repo_marker)
            self.assertIs(planner.task_manager.repository, repo_marker)
            self.assertIs(planner.calendar_manager.repository, repo_marker)
            self.assertIs(planner.task_calendar_manager.repository, repo_marker)
            self.assertIs(planner.reminder.task_repository, repo_marker)
        finally:
            main.RENDER_SOURCE = original_render_source
            main.NOTIFY_SOURCE = original_notify_source
            main._build_ydb_task_repository = original_builder


if __name__ == "__main__":
    unittest.main()

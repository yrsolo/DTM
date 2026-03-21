"""Tests for archived runtime source switching to store-backed repository."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from archive.code.legacy_runtime.entrypoints.jobs.source_switch_job import SourceSwitchRequest, apply_task_source_switches


class MainSourceSwitchTestCase(unittest.TestCase):
    def test_apply_task_source_switches_rebinds_render_and_notify(self) -> None:
        repo_marker = object()

        planner = SimpleNamespace(
            task_repository=object(),
            task_manager=SimpleNamespace(repository=object()),
            calendar_manager=SimpleNamespace(repository=object()),
            task_calendar_manager=SimpleNamespace(repository=object()),
            reminder=SimpleNamespace(task_repository=object()),
        )

        render_switched, notify_switched = apply_task_source_switches(
            SourceSwitchRequest(
                planner=planner,
                mode="test",
                render_source="ydb",
                notify_source="ydb",
                ydb_endpoint="ep",
                ydb_database="db",
                ydb_sa_json_credentials=None,
                ydb_sa_key_file=None,
                log=lambda _: None,
                repository_cls=lambda **_: repo_marker,  # type: ignore[arg-type]
            )
        )

        self.assertTrue(render_switched)
        self.assertTrue(notify_switched)
        self.assertIs(planner.task_repository, repo_marker)
        self.assertIs(planner.task_manager.repository, repo_marker)
        self.assertIs(planner.calendar_manager.repository, repo_marker)
        self.assertIs(planner.task_calendar_manager.repository, repo_marker)
        self.assertIs(planner.reminder.task_repository, repo_marker)


if __name__ == "__main__":
    unittest.main()


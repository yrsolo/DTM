"""Tests for normalized YDB task repository adapter."""

from __future__ import annotations

import unittest

import pandas as pd

from src.adapters.ydb.task_repository import YdbOperationalTaskRepository


class _RepoStub:
    def list_tasks(self, *, statuses=None):  # noqa: ANN001
        if statuses and "work" not in set(statuses):
            return []
        return [
            {
                "task_id": "1",
                "title": "Task 1",
                "owner_id": "Designer",
                "status": "work",
                "brand": "Brand",
                "format_": "Format",
                "group_id": "Project",
                "customer": "Customer",
                "raw_timing": "raw",
            }
        ]

    def list_milestones(self, *, task_ids=None, include_details=True):  # noqa: ANN001
        _ = include_details
        if task_ids and "1" not in task_ids:
            return []
        return [
            {"task_id": "1", "idx": 1, "type": "storyboard", "planned_date": "2026-03-01"},
            {"task_id": "1", "idx": 2, "type": "animatic", "planned_date": "2026-03-03"},
        ]


class _RepoStubYdbDateInt(_RepoStub):
    def list_milestones(self, *, task_ids=None, include_details=True):  # noqa: ANN001
        _ = include_details
        if task_ids and "1" not in task_ids:
            return []
        # 20419 days from 1970-01-01 -> 2025-11-27
        return [{"task_id": "1", "idx": 1, "type": "storyboard", "planned_date": 20419}]


class YdbOperationalTaskRepositoryTestCase(unittest.TestCase):
    def test_builds_task_timing_from_milestones_table(self) -> None:
        repo = YdbOperationalTaskRepository(
            endpoint="grpcs://example:2135",
            database="/db",
            repo=_RepoStub(),  # type: ignore[arg-type]
        )

        tasks = repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "1")
        self.assertIn(pd.Timestamp("2026-03-01"), tasks[0].timing)
        self.assertEqual(tasks[0].timing[pd.Timestamp("2026-03-01")], ["storyboard"])

    def test_filters_by_color_status(self) -> None:
        repo = YdbOperationalTaskRepository(
            endpoint="grpcs://example:2135",
            database="/db",
            repo=_RepoStub(),  # type: ignore[arg-type]
        )

        work_tasks = repo.get_task_by_color_status(["work"])
        done_tasks = repo.get_task_by_color_status(["done"])

        self.assertEqual(len(work_tasks), 1)
        self.assertEqual(len(done_tasks), 0)

    def test_parses_ydb_date_int_as_day_offset(self) -> None:
        repo = YdbOperationalTaskRepository(
            endpoint="grpcs://example:2135",
            database="/db",
            repo=_RepoStubYdbDateInt(),  # type: ignore[arg-type]
        )

        tasks = repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        dates = sorted(tasks[0].timing.keys())
        self.assertEqual(dates[0], pd.Timestamp("2025-11-27"))


if __name__ == "__main__":
    unittest.main()

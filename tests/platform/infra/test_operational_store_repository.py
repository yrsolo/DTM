"""Tests for store-backed repository projection."""

from __future__ import annotations

import unittest

import pandas as pd

from src.platform.infra.operational_store import StoreTaskRepository


class _Store:
    def __init__(self, rows):
        self.rows = rows

    def list_tasks(self):
        return list(self.rows)

    def upsert_tasks(self, tasks):
        _ = tasks
        return {}


class StoreTaskRepositoryTestCase(unittest.TestCase):
    def test_get_all_tasks_parses_timing(self) -> None:
        repo = StoreTaskRepository(
            _Store(
                [
                    {
                        "task_id": "1",
                        "name": "Task A",
                        "designer": "Alice",
                        "status": "work",
                        "color_status": "work",
                        "timing": [{"date": "2026-03-05", "stages": ["раскадровка"]}],
                    }
                ]
            )
        )
        tasks = repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "1")
        self.assertIn(pd.Timestamp("2026-03-05"), tasks[0].timing)

    def test_get_task_by_color_status_filters(self) -> None:
        repo = StoreTaskRepository(
            _Store(
                [
                    {"task_id": "1", "color_status": "work"},
                    {"task_id": "2", "color_status": "done"},
                ]
            )
        )
        tasks = repo.get_task_by_color_status(["work"])
        self.assertEqual([task.id for task in tasks], ["1"])

    def test_get_tasks_by_date_uses_work_subset(self) -> None:
        repo = StoreTaskRepository(
            _Store(
                [
                    {
                        "task_id": "1",
                        "color_status": "work",
                        "timing": [{"date": "2026-03-10", "stages": ["animatic"]}],
                    },
                    {
                        "task_id": "2",
                        "color_status": "done",
                        "timing": [{"date": "2026-03-10", "stages": ["final"]}],
                    },
                ]
            )
        )
        tasks = repo.get_tasks_by_date(pd.Timestamp("2026-03-10"))
        self.assertEqual([task.id for task in tasks], ["1"])


if __name__ == "__main__":
    unittest.main()

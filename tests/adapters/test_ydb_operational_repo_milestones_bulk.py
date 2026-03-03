"""Tests for safe bulk milestone replace in operational repo."""

from __future__ import annotations

import unittest

from src.adapters.ydb.operational_repo import OperationalTaskRepo


class _ClientStub:
    def __init__(self) -> None:
        self.execute_calls: list[tuple[str, dict]] = []

    def execute(self, query: str, params: dict):  # noqa: ANN001
        self.execute_calls.append((query, params))
        return []


class OperationalRepoMilestonesBulkTestCase(unittest.TestCase):
    def test_bulk_replace_deletes_only_target_task_ids(self) -> None:
        repo = OperationalTaskRepo.__new__(OperationalTaskRepo)
        repo.client = _ClientStub()
        repo.milestones_table = "dtm_task_milestones"

        payload = {
            "task-1": [{"idx": 0, "type": "storyboard", "planned": "2026-03-01"}],
            "task-2": [{"idx": 0, "type": "animatic", "planned": "2026-03-03"}],
        }
        rows = repo.replace_task_milestones_bulk(payload)

        self.assertEqual(rows, 2)
        self.assertGreaterEqual(len(repo.client.execute_calls), 2)
        delete_query = repo.client.execute_calls[0][0]
        self.assertIn("DELETE FROM `dtm_task_milestones`", delete_query)
        self.assertIn("WHERE task_id IN $task_ids", delete_query)
        self.assertNotIn("DELETE FROM `dtm_task_milestones`;", delete_query)


if __name__ == "__main__":
    unittest.main()

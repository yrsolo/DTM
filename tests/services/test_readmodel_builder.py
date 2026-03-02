"""Unit tests for read-model builder."""

from __future__ import annotations

import unittest
from datetime import date

from src.core.models.contracts import TaskNormalized
from src.services.readmodels.builder import build_read_models


class ReadModelBuilderTestCase(unittest.TestCase):
    def test_builds_views_and_summary(self) -> None:
        tasks = [
            TaskNormalized(
                task_id="t2",
                title="Task 2",
                project=None,
                designer_id="d1",
                status="work",
                stages=[],
                next_due_at=date(2026, 3, 8),
            ),
            TaskNormalized(
                task_id="t1",
                title="Task 1",
                project=None,
                designer_id="d1",
                status="pre_done",
                stages=[],
                next_due_at=date(2026, 3, 5),
            ),
            TaskNormalized(
                task_id="t3",
                title="Task 3",
                project=None,
                designer_id=None,
                status="work",
                stages=[],
                next_due_at=None,
            ),
        ]
        payload = build_read_models(tasks)

        self.assertEqual(payload["artifact"], "read_models_v1")
        self.assertEqual(payload["summary"]["tasks_total"], 3)
        self.assertEqual(payload["summary"]["designers_total"], 2)

        view_by_tasks = payload["view_by_tasks"]["tasks"]
        self.assertEqual([item["task_id"] for item in view_by_tasks], ["t1", "t2", "t3"])

        by_designer = payload["view_by_designer"]["items"]
        self.assertEqual(by_designer[0]["designer_id"], "d1")
        self.assertEqual([item["task_id"] for item in by_designer[0]["tasks"]], ["t1", "t2"])
        self.assertEqual(by_designer[1]["designer_id"], "unassigned")


if __name__ == "__main__":
    unittest.main()


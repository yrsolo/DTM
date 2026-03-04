from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.entrypoints.jobs.task_payloads import task_to_operational_payload, task_to_store_record


class _TaskStub:
    def __init__(self) -> None:
        self.id = "42"
        self.name = "Task 42"
        self.brand = "Brand"
        self.format_ = "Format"
        self.project_name = "Project"
        self.customer = "Customer"
        self.designer = "Designer"
        self.status = "work"
        self.color_status = "work"
        self.raw_timing = "raw"
        self.min_date = datetime(2026, 3, 4, tzinfo=timezone.utc)
        self.max_date = datetime(2026, 3, 11, tzinfo=timezone.utc)
        self.timing = {
            datetime(2026, 3, 4, tzinfo=timezone.utc): ["start"],
            datetime(2026, 3, 11, tzinfo=timezone.utc): ["animatic"],
        }


class TaskPayloadsJobTestCase(unittest.TestCase):
    def test_task_to_store_record(self) -> None:
        payload = task_to_store_record(_TaskStub())
        self.assertEqual(payload["task_id"], "42")
        self.assertEqual(len(payload["timing"]), 2)
        self.assertEqual(payload["timing"][0]["date"], "2026-03-04")

    def test_task_to_operational_payload(self) -> None:
        payload = task_to_operational_payload(_TaskStub())
        self.assertEqual(payload["task_id"], "42")
        self.assertEqual(payload["start_date"], "2026-03-04")
        self.assertEqual(payload["end_date"], "2026-03-11")
        self.assertEqual(len(payload["milestones"]), 2)


if __name__ == "__main__":
    unittest.main()

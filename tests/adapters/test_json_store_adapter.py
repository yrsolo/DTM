"""Unit tests for JSON operational store adapter."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.adapters.store_ydb import JsonOperationalStore


class JsonOperationalStoreTestCase(unittest.TestCase):
    def test_upsert_is_idempotent_by_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = JsonOperationalStore(Path(tmp_dir) / "store.json")

            first = [
                {"task_id": "t1", "title": "Task A", "status": "work"},
                {"task_id": "t2", "title": "Task B", "status": "work"},
            ]
            store.upsert_tasks(first)

            second = [
                {"task_id": "t1", "title": "Task A changed", "status": "pre_done"},
            ]
            payload = store.upsert_tasks(second)
            tasks = payload["tasks"]

            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks["t1"]["title"], "Task A changed")
            self.assertEqual(tasks["t2"]["title"], "Task B")


if __name__ == "__main__":
    unittest.main()


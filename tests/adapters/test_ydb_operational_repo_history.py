"""History column write/read expectations for OperationalTaskRepo."""

from __future__ import annotations

import unittest

from src.adapters.ydb.operational_repo import OperationalTaskRepo


class _ClientStub:
    def __init__(self) -> None:
        self.execute_calls: list[tuple[str, dict]] = []

    def execute(self, query: str, params: dict):  # noqa: ANN001
        self.execute_calls.append((query, params))
        return []


class OperationalRepoHistoryTestCase(unittest.TestCase):
    def test_upsert_tasks_batch_includes_history_column_and_value(self) -> None:
        repo = OperationalTaskRepo.__new__(OperationalTaskRepo)
        repo.client = _ClientStub()
        repo.tasks_table = "dtm_tasks"

        written = repo.upsert_tasks_batch(
            [
                {
                    "task_id": "42",
                    "title": "Task 42",
                    "status": "work",
                    "history": "03.03 - комментарии, отдали апдейт",
                }
            ]
        )

        self.assertEqual(written, 1)
        self.assertEqual(len(repo.client.execute_calls), 1)
        query, params = repo.client.execute_calls[0]
        self.assertIn("history:Utf8", query)
        self.assertIn("task_revision, history, raw_payload", query)
        self.assertEqual(params["$rows"][0]["history"], "03.03 - комментарии, отдали апдейт")

    def test_list_tasks_selects_history_column(self) -> None:
        class _Row:
            task_id = "42"
            title = "Task 42"
            brand = "Brand"
            format_ = "Format"
            customer = "Customer"
            raw_timing = "raw"
            owner_id = "owner"
            group_id = "group"
            status = "work"
            start_date = None
            end_date = None
            next_due_date = None
            history = "raw status timeline"
            tags_json = "[]"
            links_json = "{}"
            task_hash = "hash"
            task_revision = 1
            raw_payload = "{}"
            updated_at_utc = None

        class _ResultSet:
            rows = [_Row()]

        repo = OperationalTaskRepo.__new__(OperationalTaskRepo)
        repo.client = _ClientStub()
        repo.tasks_table = "dtm_tasks"
        repo.client.execute = lambda query, params: [_ResultSet()]  # type: ignore[method-assign]

        rows = repo.list_tasks(statuses=["work"])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["history"], "raw status timeline")


if __name__ == "__main__":
    unittest.main()

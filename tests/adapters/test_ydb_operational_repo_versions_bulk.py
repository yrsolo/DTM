"""Bulk version write/archive expectations for OperationalTaskRepo."""

from __future__ import annotations

import unittest

from src.adapters.ydb.operational_repo import OperationalTaskRepo


class _ClientStub:
    def __init__(self) -> None:
        self.execute_calls: list[tuple[str, dict]] = []

    def execute(self, query: str, params: dict):  # noqa: ANN001
        self.execute_calls.append((query, params))
        return []


class OperationalRepoVersionsBulkTestCase(unittest.TestCase):
    def _build_repo(self) -> tuple[OperationalTaskRepo, _ClientStub]:
        repo = OperationalTaskRepo.__new__(OperationalTaskRepo)
        client = _ClientStub()
        repo.client = client
        repo.versions_table = "dtm_task_versions"
        return repo, client

    def test_upsert_task_versions_bulk_writes_expected_fields(self) -> None:
        repo, client = self._build_repo()

        written = repo.upsert_task_versions_bulk(
            [
                {
                    "task_id": "task-1",
                    "version": 2,
                    "status": "active",
                    "content_hash": "sha256:abc",
                    "payload_json": '{"task_id":"task-1"}',
                }
            ]
        )

        self.assertEqual(written, 1)
        self.assertEqual(len(client.execute_calls), 1)
        query, params = client.execute_calls[0]
        self.assertIn("UPSERT INTO `dtm_task_versions`", query)
        self.assertIn("content_hash:Utf8", query)
        self.assertEqual(params["$rows"][0]["task_id"], "task-1")
        self.assertEqual(params["$rows"][0]["version"], 2)

    def test_archive_task_versions_bulk_writes_batch_rows(self) -> None:
        repo, client = self._build_repo()

        archived = repo.archive_task_versions_bulk(
            [
                {"task_id": "task-1", "version": 1},
                {"task_id": "task-2", "version": 3},
            ]
        )

        self.assertEqual(archived, 2)
        self.assertEqual(len(client.execute_calls), 1)
        query, params = client.execute_calls[0]
        self.assertIn("UPSERT INTO `dtm_task_versions` (task_id, version, status)", query)
        self.assertEqual(len(params["$rows"]), 2)

    def test_upsert_task_versions_bulk_chunks_large_payload(self) -> None:
        repo, client = self._build_repo()
        rows = [
            {
                "task_id": f"task-{idx}",
                "version": 1,
                "status": "active",
                "content_hash": f"hash-{idx}",
                "payload_json": "{}",
            }
            for idx in range(450)
        ]

        written = repo.upsert_task_versions_bulk(rows)

        self.assertEqual(written, 450)
        self.assertEqual(len(client.execute_calls), 3)
        chunk_sizes = [len(call[1]["$rows"]) for call in client.execute_calls]
        self.assertEqual(chunk_sizes, [200, 200, 50])


if __name__ == "__main__":
    unittest.main()

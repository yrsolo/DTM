"""Tests for source-range hash gate behavior in YDB sync service."""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.services.sync_service import YdbSyncService, stable_json_hash


@dataclass
class _StateRow:
    source_hash: str


class _RepoStub:
    def __init__(self) -> None:
        self._state: _StateRow | None = None
        self.stats = type("Stats", (), {"ydb_queries_count": 0, "error_code": ""})()
        self.client = type("Client", (), {"stats": self.stats})()
        self.upsert_calls = 0
        self.milestone_replace_calls = 0

    def get_sync_state(self, source_id: str):  # noqa: ARG002
        return self._state

    def set_sync_state(self, source_id: str, source_hash: str, *, last_error: str | None = None):  # noqa: ARG002
        self._state = _StateRow(source_hash=source_hash)

    def upsert_tasks_batch(self, tasks):  # noqa: ANN001
        self.upsert_calls += 1
        return len(tasks)

    def replace_task_milestones_bulk(self, payload_by_task):  # noqa: ANN001
        self.milestone_replace_calls += 1
        return sum(len(items) for items in payload_by_task.values())


class SyncSourceHashGateTestCase(unittest.TestCase):
    def test_stable_json_hash_changes_on_values_update(self) -> None:
        values_a = [["id", "status"], ["1", "work"]]
        values_b = [["id", "status"], ["1", "pre_done"]]
        self.assertNotEqual(stable_json_hash(values_a), stable_json_hash(values_b))

    def test_sync_skips_upsert_when_source_hash_unchanged(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo)  # type: ignore[arg-type]
        source_values = [["id", "status"], ["1", "work"]]
        normalized = [{"task_id": "1", "status": "work", "milestones": []}]

        first = service.run(
            source_id="sheet:test",
            source_range_values=source_values,
            normalized_tasks=normalized,
        )
        second = service.run(
            source_id="sheet:test",
            source_range_values=source_values,
            normalized_tasks=normalized,
        )

        self.assertFalse(first.no_changes)
        self.assertTrue(second.no_changes)
        self.assertEqual(repo.upsert_calls, 1)
        self.assertEqual(repo.milestone_replace_calls, 1)


if __name__ == "__main__":
    unittest.main()


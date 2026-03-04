"""Tests for source-range gate, versioning rules, and forced refresh behavior."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from datetime import datetime, timezone

from src.services.sync_service import YdbSyncService, stable_json_hash


@dataclass
class _StateRow:
    preflight_hash_50: str
    source_hash_full: str
    last_full_sync_at_utc: datetime
    last_success_at_utc: datetime

    @property
    def source_hash(self) -> str:
        return self.source_hash_full


class _RepoStub:
    def __init__(self) -> None:
        self._state: _StateRow | None = None
        self.stats = type("Stats", (), {"ydb_queries_count": 0, "error_code": ""})()
        self.client = type("Client", (), {"stats": self.stats})()
        self.upsert_calls = 0
        self.milestone_replace_calls = 0
        self.milestone_version_upserts = 0
        self.version_upserts = 0
        self.version_archives = 0
        self.force_empty_versioned_write = False
        self.versioned_rows_by_key = {}
        self._tasks = {}

    def get_sync_state(self, source_id: str):  # noqa: ARG002
        return self._state

    def set_sync_state(self, **kwargs):  # noqa: ANN003
        now = kwargs.get("last_success_at_utc") or datetime.now(timezone.utc)
        self._state = _StateRow(
            preflight_hash_50=str(kwargs.get("preflight_hash_50", "")),
            source_hash_full=str(kwargs.get("source_hash_full", "")),
            last_full_sync_at_utc=kwargs.get("last_full_sync_at_utc") or now,
            last_success_at_utc=now,
        )

    def list_tasks(self, *, statuses=None):  # noqa: ANN001, ARG002
        return list(self._tasks.values())

    def upsert_tasks_batch(self, tasks):  # noqa: ANN001
        self.upsert_calls += 1
        for task in tasks:
            self._tasks[str(task["task_id"])] = {
                "task_id": str(task["task_id"]),
                "task_hash": str(task.get("task_hash", "")),
                "task_revision": int(task.get("task_revision", 0) or 0),
                "current_version": int(task.get("task_revision", 0) or 0),
            }
        return len(tasks)

    def replace_task_milestones_bulk(self, payload_by_task):  # noqa: ANN001
        self.milestone_replace_calls += 1
        return sum(len(items) for items in payload_by_task.values())

    def upsert_task_milestones_versions_bulk(self, payload_by_task_version):  # noqa: ANN001
        self.milestone_version_upserts += 1
        if self.force_empty_versioned_write:
            return 0
        for key, rows in payload_by_task_version.items():
            self.versioned_rows_by_key[key] = list(rows)
        return sum(len(items) for items in payload_by_task_version.values())

    def list_milestones_for_versions(self, *, task_versions, include_details=True):  # noqa: ANN001, ARG002
        rows = []
        for task_id, version in task_versions.items():
            for row in self.versioned_rows_by_key.get((task_id, version), []):
                payload = dict(row)
                payload["task_id"] = task_id
                payload["version"] = version
                rows.append(payload)
        return rows

    def archive_task_version(self, *, task_id, version):  # noqa: ANN001, ARG002
        self.version_archives += 1

    def upsert_task_version(self, **kwargs):  # noqa: ANN003
        self.version_upserts += 1


class SyncSourceHashGateTestCase(unittest.TestCase):
    def test_stable_json_hash_changes_on_values_update(self) -> None:
        values_a = [["id", "status"], ["1", "work"]]
        values_b = [["id", "status"], ["1", "pre_done"]]
        self.assertNotEqual(stable_json_hash(values_a), stable_json_hash(values_b))

    def test_sync_skips_full_sync_when_preflight_unchanged_and_recent(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo, write_legacy_milestones=True)  # type: ignore[arg-type]
        snapshot = {"values": [["id"], ["1"]], "colors": ["#fff"]}
        normalized = [{"task_id": "1", "title": "A", "status": "work", "milestones": []}]

        first = service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot,
            source_range_values=snapshot,
            normalized_tasks=normalized,
        )
        second = service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot,
            source_range_values=snapshot,
            normalized_tasks=normalized,
        )

        self.assertFalse(first.no_changes)
        self.assertTrue(second.no_changes)
        self.assertFalse(second.full_sync_performed)
        self.assertEqual(repo.upsert_calls, 1)
        self.assertEqual(repo.milestone_replace_calls, 1)

    def test_color_only_change_does_not_increment_version(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo, write_legacy_milestones=True)  # type: ignore[arg-type]
        preflight_a = {"values": [["id"], ["1"]], "colors": ["#fff"]}
        full_a = {"values": [["id", "title"], ["1", "Task"]], "colors": ["#fff"]}
        full_b = {"values": [["id", "title"], ["1", "Task"]], "colors": ["#000"]}
        normalized = [{"task_id": "1", "title": "Task", "status": "work", "milestones": []}]

        first = service.run(
            source_id="sheet:test",
            preflight_range_values=preflight_a,
            source_range_values=full_a,
            normalized_tasks=normalized,
        )
        second = service.run(
            source_id="sheet:test",
            preflight_range_values={"values": [["id"], ["1"]], "colors": ["#000"]},
            source_range_values=full_b,
            normalized_tasks=normalized,
        )

        self.assertEqual(first.tasks_upserted, 1)
        self.assertEqual(second.tasks_upserted, 1)
        self.assertEqual(repo._tasks["1"]["task_revision"], 1)
        self.assertEqual(repo.version_upserts, 1)
        self.assertEqual(repo.version_archives, 0)
        self.assertEqual(repo.milestone_version_upserts, 1)

    def test_content_change_increments_version_and_archives_previous(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo, write_legacy_milestones=True)  # type: ignore[arg-type]
        snapshot_a = {"values": [["id"], ["1"]], "colors": ["#fff"]}
        full_a = {"values": [["id", "title"], ["1", "Task"]], "colors": ["#fff"]}
        full_b = {"values": [["id", "title"], ["1", "Task 2"]], "colors": ["#fff"]}

        service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot_a,
            source_range_values=full_a,
            normalized_tasks=[{"task_id": "1", "title": "Task", "status": "work", "milestones": []}],
        )
        service.run(
            source_id="sheet:test",
            preflight_range_values={"values": [["id"], ["1"]], "colors": ["#aaa"]},
            source_range_values=full_b,
            normalized_tasks=[{"task_id": "1", "title": "Task 2", "status": "work", "milestones": []}],
        )

        self.assertEqual(repo._tasks["1"]["task_revision"], 2)
        self.assertEqual(repo.version_upserts, 2)
        self.assertEqual(repo.version_archives, 1)
        self.assertEqual(repo.milestone_version_upserts, 2)

    def test_history_change_increments_version(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo, write_legacy_milestones=True)  # type: ignore[arg-type]
        snapshot_a = {"values": [["id"], ["1"]], "colors": ["#fff"]}
        full_a = {"values": [["id", "title"], ["1", "Task"]], "colors": ["#fff"]}
        full_b = {"values": [["id", "title"], ["1", "Task"]], "colors": ["#aaa"]}

        service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot_a,
            source_range_values=full_a,
            normalized_tasks=[
                {"task_id": "1", "title": "Task", "status": "work", "history": "raw A", "milestones": []}
            ],
        )
        service.run(
            source_id="sheet:test",
            preflight_range_values={"values": [["id"], ["1"]], "colors": ["#aaa"]},
            source_range_values=full_b,
            normalized_tasks=[
                {"task_id": "1", "title": "Task", "status": "work", "history": "raw B", "milestones": []}
            ],
        )

        self.assertEqual(repo._tasks["1"]["task_revision"], 2)
        self.assertEqual(repo.version_upserts, 2)
        self.assertEqual(repo.version_archives, 1)

    def test_forced_refresh_does_not_change_existing_version(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo, write_legacy_milestones=True)  # type: ignore[arg-type]
        snapshot = {"values": [["id"], ["1"]], "colors": ["#fff"]}
        full_a = {"values": [["id", "title"], ["1", "Task"]], "colors": ["#fff"]}
        full_b = {"values": [["id", "title"], ["1", "Task changed"]], "colors": ["#fff"]}

        service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot,
            source_range_values=full_a,
            normalized_tasks=[{"task_id": "1", "title": "Task", "status": "work", "milestones": []}],
        )
        service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot,
            source_range_values=full_b,
            normalized_tasks=[{"task_id": "1", "title": "Task changed", "status": "work", "milestones": []}],
            force_refresh=True,
        )

        self.assertEqual(repo._tasks["1"]["task_revision"], 1)
        self.assertEqual(repo.version_upserts, 1)
        self.assertEqual(repo.version_archives, 0)
        self.assertEqual(repo.milestone_version_upserts, 1)

    def test_start_milestone_is_added_when_missing(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo, write_legacy_milestones=True)  # type: ignore[arg-type]
        snapshot = {"values": [["id"], ["1"]], "colors": ["#fff"]}

        result = service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot,
            source_range_values=snapshot,
            normalized_tasks=[{"task_id": "1", "title": "Task", "status": "work", "milestones": []}],
        )

        self.assertEqual(result.milestones_upserted, 1)

    def test_legacy_milestones_write_disabled_by_default(self) -> None:
        repo = _RepoStub()
        service = YdbSyncService(repo)  # type: ignore[arg-type]
        snapshot = {"values": [["id"], ["1"]], "colors": ["#fff"]}

        service.run(
            source_id="sheet:test",
            preflight_range_values=snapshot,
            source_range_values=snapshot,
            normalized_tasks=[{"task_id": "1", "title": "Task", "status": "work", "milestones": []}],
        )

        self.assertEqual(repo.milestone_replace_calls, 0)

    def test_sync_fails_when_versioned_milestones_write_returns_zero(self) -> None:
        repo = _RepoStub()
        repo.force_empty_versioned_write = True
        service = YdbSyncService(repo)  # type: ignore[arg-type]
        snapshot = {"values": [["id"], ["1"]], "colors": ["#fff"]}

        with self.assertRaises(RuntimeError) as ctx:
            service.run(
                source_id="sheet:test",
                preflight_range_values=snapshot,
                source_range_values=snapshot,
                normalized_tasks=[{"task_id": "1", "title": "Task", "status": "work", "milestones": []}],
            )
        self.assertIn("milestones_write_empty", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

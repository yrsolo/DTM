from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.platform.runtime.commands.model import Command, RequestedBy
from src.platform.runtime.worker.model import JobResult
from src.platform.runtime.worker.status_store import S3JobStatusStore


class _MemoryStatusStore(S3JobStatusStore):
    def __init__(self) -> None:
        self._memory: dict[str, dict] = {}
        super().__init__(
            bucket="dtm",
            endpoint_url=None,
            aws_access_key_id=None,
            aws_secret_access_key=None,
            status_prefix="jobs/test/status/",
            latest_prefix="jobs/test/latest/",
        )
        self._history_limit = 3
        self._history_per_command_limit = 2

    def _put_json(self, key: str, payload: dict):  # type: ignore[override]
        self._memory[key] = dict(payload)

    def _get_json(self, key: str):  # type: ignore[override]
        value = self._memory.get(key)
        return None if value is None else dict(value)

    def _delete_key(self, key: str) -> None:  # type: ignore[override]
        self._memory.pop(key, None)

    def _list_status_keys(self) -> list[str]:  # type: ignore[override]
        return sorted(key for key in self._memory if key.startswith("jobs/test/status/"))


class JobStatusStoreHistoryTestCase(unittest.TestCase):
    def test_put_finished_appends_terminal_history_only(self) -> None:
        store = _MemoryStatusStore()
        cmd = Command(
            job_id="job-1",
            type="update_snapshot",
            created_at_utc=datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc),
            requested_by=RequestedBy(source="admin"),
        )
        store.put_queued(cmd)
        self.assertEqual(store.get_recent(), [])

        store.put_finished(cmd, JobResult(success=True, details={"artifact": "update_snapshot"}))
        recent = store.get_recent()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].job_id, "job-1")
        self.assertEqual(recent[0].status, "success")

    def test_history_is_trimmed_newest_first(self) -> None:
        store = _MemoryStatusStore()
        base = datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc)
        for idx in range(4):
            cmd = Command(
                job_id=f"job-{idx}",
                type="render_timeline_sheet" if idx % 2 == 0 else "update_snapshot",
                created_at_utc=base + timedelta(minutes=idx),
                requested_by=RequestedBy(source="admin"),
            )
            store.put_finished(
                cmd,
                JobResult(
                    success=(idx % 2 == 0),
                    retryable=(idx % 2 == 1),
                    details={"idx": idx},
                ),
            )

        recent = store.get_recent()
        self.assertEqual([item.job_id for item in recent], ["job-3", "job-2", "job-1"])

    def test_history_by_command_is_trimmed_independently(self) -> None:
        store = _MemoryStatusStore()
        base = datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc)
        for idx in range(3):
            cmd = Command(
                job_id=f"render-{idx}",
                type="render_timeline_sheet",
                created_at_utc=base + timedelta(minutes=idx),
                requested_by=RequestedBy(source="admin"),
            )
            store.put_finished(cmd, JobResult(success=True, details={"idx": idx}))

        by_command = store.get_recent_by_command("render_timeline_sheet")
        self.assertEqual([item.job_id for item in by_command], ["render-2", "render-1"])

    def test_failed_retryable_is_persisted_with_retryable_flag(self) -> None:
        store = _MemoryStatusStore()
        cmd = Command(
            job_id="job-retryable",
            type="send_reminders",
            created_at_utc=datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc),
            requested_by=RequestedBy(source="trigger"),
        )

        store.put_finished(
            cmd,
            JobResult(
                success=False,
                retryable=True,
                failure_kind="retryable",
                error_code="telegram_timeout",
                details={"artifact": "send_reminders"},
                error={"code": "telegram_timeout"},
            ),
        )

        stored = store.get("job-retryable")
        self.assertIsNotNone(stored)
        self.assertEqual(stored.status, "failed_retryable")
        self.assertTrue(stored.retryable)

    def test_prune_terminal_statuses_before_deletes_only_old_terminal_records(self) -> None:
        store = _MemoryStatusStore()
        old = datetime(2026, 3, 9, 8, 0, tzinfo=timezone.utc)
        recent = datetime(2026, 3, 9, 12, 0, tzinfo=timezone.utc)
        store._memory["jobs/test/status/success-old.json"] = {
            "job_id": "success-old",
            "command_type": "update_snapshot",
            "status": "success",
            "requested_at_utc": "2026-03-09T07:00:00Z",
            "finished_at_utc": "2026-03-09T08:00:00Z",
        }
        store._memory["jobs/test/status/running.json"] = {
            "job_id": "running",
            "command_type": "update_snapshot",
            "status": "running",
            "requested_at_utc": "2026-03-09T07:00:00Z",
        }
        store._memory["jobs/test/status/failed-no-finished.json"] = {
            "job_id": "failed-no-finished",
            "command_type": "send_reminders",
            "status": "failed_terminal",
            "requested_at_utc": "2026-03-09T07:00:00Z",
        }
        store._memory["jobs/test/status/success-recent.json"] = {
            "job_id": "success-recent",
            "command_type": "render_timeline_sheet",
            "status": "success",
            "requested_at_utc": "2026-03-09T11:00:00Z",
            "finished_at_utc": "2026-03-09T12:00:00Z",
        }
        store._memory["jobs/test/latest/update_snapshot.json"] = {"job_id": "latest"}
        store._memory["jobs/test/history/index.json"] = {"items": [{"job_id": "history"}]}

        summary = store.prune_terminal_statuses_before(datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc))

        self.assertEqual(summary["scanned"], 4)
        self.assertEqual(summary["eligible"], 1)
        self.assertEqual(summary["deleted"], 1)
        self.assertEqual(summary["kept_non_terminal"], 1)
        self.assertEqual(summary["kept_without_finished_at"], 1)
        self.assertNotIn("jobs/test/status/success-old.json", store._memory)
        self.assertIn("jobs/test/status/running.json", store._memory)
        self.assertIn("jobs/test/status/failed-no-finished.json", store._memory)
        self.assertIn("jobs/test/status/success-recent.json", store._memory)
        self.assertIn("jobs/test/latest/update_snapshot.json", store._memory)
        self.assertIn("jobs/test/history/index.json", store._memory)

    def test_prune_terminal_statuses_before_honors_dry_run(self) -> None:
        store = _MemoryStatusStore()
        store._memory["jobs/test/status/success-old.json"] = {
            "job_id": "success-old",
            "command_type": "update_snapshot",
            "status": "success",
            "requested_at_utc": "2026-03-09T07:00:00Z",
            "finished_at_utc": "2026-03-09T08:00:00Z",
        }

        summary = store.prune_terminal_statuses_before(
            datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc),
            dry_run=True,
        )

        self.assertEqual(summary["eligible"], 1)
        self.assertEqual(summary["deleted"], 0)
        self.assertTrue(summary["dry_run"])
        self.assertIn("jobs/test/status/success-old.json", store._memory)

    def test_prune_terminal_statuses_before_honors_limit(self) -> None:
        store = _MemoryStatusStore()
        for idx in range(3):
            store._memory[f"jobs/test/status/success-{idx}.json"] = {
                "job_id": f"success-{idx}",
                "command_type": "update_snapshot",
                "status": "success",
                "requested_at_utc": "2026-03-09T07:00:00Z",
                "finished_at_utc": f"2026-03-09T08:0{idx}:00Z",
            }

        summary = store.prune_terminal_statuses_before(
            datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc),
            limit=2,
        )

        self.assertEqual(summary["eligible"], 2)
        self.assertEqual(summary["deleted"], 2)
        self.assertTrue(summary["limit_reached"])
        remaining = [key for key in store._memory if key.startswith("jobs/test/status/")]
        self.assertEqual(len(remaining), 1)


if __name__ == "__main__":
    unittest.main()


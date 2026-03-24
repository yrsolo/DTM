from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from src.platform.errors import UserError
from src.platform.runtime.commands.model import Command, RequestedBy
from src.platform.runtime.maintenance.job_status_cleanup_job import CleanupJobStatusesJob


class _FakeStatusStore:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def prune_terminal_statuses_before(self, delete_before_utc, *, dry_run=False, limit=None):
        self.calls.append(
            {
                "delete_before_utc": delete_before_utc,
                "dry_run": dry_run,
                "limit": limit,
            }
        )
        return {
            "scanned": 10,
            "eligible": 2,
            "deleted": 2,
            "kept_non_terminal": 5,
            "kept_without_finished_at": 1,
            "dry_run": dry_run,
            "delete_before_utc": delete_before_utc.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        }


class CleanupJobStatusesJobTestCase(unittest.TestCase):
    def _command(self, payload: dict) -> Command:
        return Command(
            job_id="job-1",
            type="cleanup_job_statuses",
            created_at_utc=datetime(2026, 3, 22, 8, 0, tzinfo=timezone.utc),
            requested_by=RequestedBy(source="trigger"),
            payload=payload,
        )

    def _job(self, status_store=None) -> CleanupJobStatusesJob:
        return CleanupJobStatusesJob(SimpleNamespace(deps={"job_status_store": status_store}))

    def test_run_uses_explicit_delete_before_utc(self) -> None:
        store = _FakeStatusStore()
        result = self._job(store).run(
            self._command({"delete_before_utc": "2026-03-21T08:00:00Z", "dry_run": True, "limit": 5})
        )

        self.assertEqual(result["artifact"], "cleanup_job_statuses")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(store.calls[0]["limit"], 5)
        self.assertTrue(store.calls[0]["dry_run"])
        self.assertEqual(store.calls[0]["delete_before_utc"].isoformat().replace("+00:00", "Z"), "2026-03-21T08:00:00Z")

    def test_run_converts_older_than_hours_to_cutoff(self) -> None:
        store = _FakeStatusStore()
        before = datetime.now(timezone.utc)
        self._job(store).run(self._command({"older_than_hours": 24}))
        after = datetime.now(timezone.utc)

        cutoff = store.calls[0]["delete_before_utc"]
        self.assertGreaterEqual(cutoff, before.replace(microsecond=0) - timedelta(hours=24, seconds=1))
        self.assertLessEqual(cutoff, after + timedelta(seconds=1) - timedelta(hours=24))

    def test_run_rejects_missing_cutoff(self) -> None:
        with self.assertRaises(UserError) as ctx:
            self._job(_FakeStatusStore()).run(self._command({}))
        self.assertEqual(ctx.exception.code, "cleanup_job_statuses_cutoff_required")

    def test_run_rejects_conflicting_cutoff_inputs(self) -> None:
        with self.assertRaises(UserError) as ctx:
            self._job(_FakeStatusStore()).run(
                self._command({"delete_before_utc": "2026-03-21T08:00:00Z", "older_than_hours": 24})
            )
        self.assertEqual(ctx.exception.code, "cleanup_job_statuses_payload_conflict")

    def test_run_rejects_invalid_delete_before_utc(self) -> None:
        with self.assertRaises(UserError) as ctx:
            self._job(_FakeStatusStore()).run(self._command({"delete_before_utc": "not-a-date"}))
        self.assertEqual(ctx.exception.code, "cleanup_job_statuses_delete_before_invalid")

    def test_run_rejects_invalid_older_than_hours(self) -> None:
        with self.assertRaises(UserError) as ctx:
            self._job(_FakeStatusStore()).run(self._command({"older_than_hours": 0}))
        self.assertEqual(ctx.exception.code, "cleanup_job_statuses_older_than_invalid")

    def test_run_rejects_invalid_limit(self) -> None:
        with self.assertRaises(UserError) as ctx:
            self._job(_FakeStatusStore()).run(self._command({"older_than_hours": 24, "limit": -1}))
        self.assertEqual(ctx.exception.code, "cleanup_job_statuses_limit_invalid")

    def test_run_requires_status_store(self) -> None:
        with self.assertRaises(UserError) as ctx:
            self._job(None).run(self._command({"older_than_hours": 24}))
        self.assertEqual(ctx.exception.code, "job_status_store_unavailable")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import asyncio
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.commands.model import Command, RequestedBy
from src.commands.serializer import command_to_json
from src.platform.errors import PermanentError, TransientError
from src.worker.model import JobResult, JobStatusRecord
from src.worker.worker import Worker


class _FakeStatusStore:
    def __init__(self) -> None:
        self.records: dict[str, JobStatusRecord] = {}

    def get(self, job_id: str) -> JobStatusRecord | None:
        return self.records.get(job_id)

    def put_running(self, cmd: Command) -> JobStatusRecord:
        record = JobStatusRecord(
            job_id=cmd.job_id,
            command_type=cmd.type,
            status="running",
            requested_at_utc=cmd.created_at_utc,
            started_at_utc=datetime.now(timezone.utc),
            requested_by={"source": cmd.requested_by.source},
        )
        self.records[cmd.job_id] = record
        return record

    def put_finished(self, cmd: Command, result: JobResult) -> JobStatusRecord:
        status = "success" if result.success else ("failed_retryable" if result.retryable else "failed_terminal")
        record = JobStatusRecord(
            job_id=cmd.job_id,
            command_type=cmd.type,
            status=status,
            requested_at_utc=cmd.created_at_utc,
            finished_at_utc=datetime.now(timezone.utc),
            requested_by={"source": cmd.requested_by.source},
            summary=dict(result.details),
            warnings=list(result.warnings),
            retryable=bool(result.retryable),
            error=dict(result.error or {}) if result.error else None,
        )
        self.records[cmd.job_id] = record
        return record


class _DispatcherReturns:
    def __init__(self, result: JobResult) -> None:
        self._result = result

    async def dispatch(self, _cmd: Command) -> JobResult:
        return self._result


class _DispatcherRaisesTransient:
    async def dispatch(self, _cmd: Command) -> JobResult:
        raise TransientError("temporary", code="temporary_failure")


class _DispatcherRaisesTerminal:
    async def dispatch(self, _cmd: Command) -> JobResult:
        raise PermanentError("broken", code="broken_payload")


def _message(job_id: str = "job-1", command_type: str = "update_snapshot") -> SimpleNamespace:
    cmd = Command(
        job_id=job_id,
        type=command_type,
        created_at_utc=datetime(2026, 3, 9, 12, 0, tzinfo=timezone.utc),
        requested_by=RequestedBy(source="trigger"),
    )
    return SimpleNamespace(raw_body=command_to_json(cmd))


class WorkerRetrySemanticsTestCase(unittest.TestCase):
    def test_retryable_failure_sets_retry_requested(self) -> None:
        store = _FakeStatusStore()
        worker = Worker(store, _DispatcherRaisesTransient(), logger=lambda *_args, **_kwargs: None)

        result = asyncio.run(worker.run_once_from_messages([_message()]))

        self.assertEqual(result["status"], "retryable_failure")
        self.assertTrue(result["retry_requested"])
        self.assertEqual(result["retryable_failed"], 1)
        self.assertEqual(store.records["job-1"].status, "failed_retryable")
        self.assertTrue(store.records["job-1"].retryable)

    def test_terminal_failure_does_not_request_retry(self) -> None:
        store = _FakeStatusStore()
        worker = Worker(store, _DispatcherRaisesTerminal(), logger=lambda *_args, **_kwargs: None)

        result = asyncio.run(worker.run_once_from_messages([_message()]))

        self.assertEqual(result["status"], "partial_failure")
        self.assertFalse(result["retry_requested"])
        self.assertEqual(result["terminal_failed"], 1)
        self.assertEqual(store.records["job-1"].status, "failed_terminal")
        self.assertFalse(store.records["job-1"].retryable)

    def test_duplicate_success_is_soft_skipped(self) -> None:
        store = _FakeStatusStore()
        store.records["job-1"] = JobStatusRecord(
            job_id="job-1",
            command_type="update_snapshot",
            status="success",
            requested_at_utc=datetime(2026, 3, 9, 12, 0, tzinfo=timezone.utc),
            requested_by={"source": "trigger"},
        )
        worker = Worker(
            store,
            _DispatcherReturns(JobResult(success=True, details={"artifact": "update_snapshot"})),
            logger=lambda *_args, **_kwargs: None,
        )

        result = asyncio.run(worker.run_once_from_messages([_message()]))

        self.assertEqual(result["skipped_duplicates"], 1)
        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["succeeded"], 0)

    def test_malformed_payload_is_terminal_failure(self) -> None:
        store = _FakeStatusStore()
        worker = Worker(store, _DispatcherReturns(JobResult(success=True)), logger=lambda *_args, **_kwargs: None)

        result = asyncio.run(worker.run_once_from_messages([SimpleNamespace(raw_body="{bad json")]))

        self.assertEqual(result["terminal_failed"], 1)
        self.assertFalse(result["retry_requested"])


if __name__ == "__main__":
    unittest.main()

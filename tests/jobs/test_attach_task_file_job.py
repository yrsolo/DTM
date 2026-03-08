from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.jobs.attach_task_file_job import AttachTaskFileJob


class _FakeEngine:
    def __init__(self) -> None:
        self.calls = []

    def attach_file_metadata(self, *, task_id, attachment):  # noqa: ANN001
        self.calls.append((task_id, attachment))
        return {
            "artifact": "attach_task_file",
            "status": "ok",
            "task_id": task_id,
            "attachment_id": attachment.id,
            "attachments_total": 1,
            "prep_written": True,
        }


class AttachTaskFileJobTestCase(unittest.TestCase):
    def test_attach_job_validates_payload_and_updates_snapshot(self) -> None:
        import src.jobs.attach_task_file_job as module

        original = module.build_snapshot_engine
        engine = _FakeEngine()
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        try:
            ctx = AppContext(cfg=SimpleNamespace(), deps={})
            cmd = Command(
                job_id="job-1",
                type="attach_task_file",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={
                    "task_id": "task-1",
                    "key": "attachments/test/task-1/a1-file.pdf",
                    "filename": "file.pdf",
                    "mime": "application/pdf",
                    "size": 123,
                    "uploaded_by": "tester",
                },
            )
            result = AttachTaskFileJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["task_id"], "task-1")
        self.assertEqual(len(engine.calls), 1)
        self.assertEqual(engine.calls[0][1].filename, "file.pdf")

    def test_attach_job_returns_failed_result_on_missing_required_field(self) -> None:
        ctx = AppContext(cfg=SimpleNamespace(), deps={})
        cmd = Command(
            job_id="job-2",
            type="attach_task_file",
            created_at_utc=datetime.now(timezone.utc),
            requested_by=RequestedBy(source="admin"),
            payload={"task_id": "task-1"},
        )
        result = AttachTaskFileJob(ctx).run(cmd)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["code"], "key_required")


if __name__ == "__main__":
    unittest.main()

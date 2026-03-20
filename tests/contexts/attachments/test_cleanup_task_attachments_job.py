from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.contexts.attachments.internal.job_runners import CleanupTaskAttachmentsJob


class _FakeEngine:
    def __init__(self) -> None:
        self.calls = []

    def cleanup_stale_attachments(self, **kwargs):  # noqa: ANN001
        self.calls.append(kwargs)
        return {
            "artifact": "cleanup_task_attachments",
            "status": "ok",
            "pending_removed": 1,
            "uploaded_unverified_removed": 0,
            "deleted_removed": 0,
            "tasks_touched": 1,
            "prep_written": True,
            "warnings": [],
        }


class _FakeStorage:
    def delete_object(self, *, key):  # noqa: ANN001
        return None


class CleanupTaskAttachmentsJobTestCase(unittest.TestCase):
    def test_cleanup_job_delegates_to_engine(self) -> None:
        import src.contexts.attachments.internal.job_runners as module

        original_engine = module.build_snapshot_engine
        original_storage = module.build_attachment_storage
        engine = _FakeEngine()
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        module.build_attachment_storage = lambda _ctx: _FakeStorage()  # type: ignore[assignment]
        try:
            ctx = AppContext(cfg=SimpleNamespace(), deps={})
            cmd = Command(
                job_id="job-1",
                type="cleanup_task_attachments",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={"ttl_seconds": 7200},
            )
            result = CleanupTaskAttachmentsJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original_engine  # type: ignore[assignment]
            module.build_attachment_storage = original_storage  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["ttl_seconds"], 7200)
        self.assertEqual(engine.calls[0]["ttl_seconds"], 7200)
        self.assertTrue(callable(engine.calls[0]["delete_object"]))

    def test_cleanup_job_rejects_invalid_ttl(self) -> None:
        ctx = AppContext(cfg=SimpleNamespace(), deps={})
        cmd = Command(
            job_id="job-2",
            type="cleanup_task_attachments",
            created_at_utc=datetime.now(timezone.utc),
            requested_by=RequestedBy(source="admin"),
            payload={"ttl_seconds": 0},
        )
        result = CleanupTaskAttachmentsJob(ctx).run(cmd)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["code"], "ttl_seconds_invalid")


if __name__ == "__main__":
    unittest.main()

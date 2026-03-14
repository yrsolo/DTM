from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.jobs.delete_task_attachment_job import DeleteTaskAttachmentJob


class _FakeMetadataStore:
    def __init__(self) -> None:
        self.pending_calls = []
        self.deleted_calls = []

    def get_by_attachment_id(self, attachment_id):  # noqa: ANN001
        if attachment_id != "a1":
            return None
        return (
            "task-1",
            SimpleNamespace(storage_key="attachments/test/task-1/a1-spec-final.docx"),
        )

    def mark_delete_pending(self, **kwargs):  # noqa: ANN001
        self.pending_calls.append(kwargs)

    def mark_deleted(self, **kwargs):  # noqa: ANN001
        self.deleted_calls.append(kwargs)


class _FakeEngine:
    def __init__(self) -> None:
        self.metadata_store = _FakeMetadataStore()
        self.delete_calls = []

    def get_attachment_metadata_store(self):
        return self.metadata_store

    def delete_attachment(self, *, task_id, attachment_id):  # noqa: ANN001
        self.delete_calls.append((task_id, attachment_id))
        return {
            "artifact": "delete_task_attachment",
            "status": "ok",
            "task_id": task_id,
            "attachment_id": attachment_id,
            "attachments_total": 0,
            "prep_written": True,
        }


class _FakeStorage:
    def __init__(self) -> None:
        self.deleted_keys = []

    def delete_object(self, *, key):  # noqa: ANN001
        self.deleted_keys.append(key)


class DeleteTaskAttachmentJobTestCase(unittest.TestCase):
    def test_delete_job_marks_deleted_and_rebuilds_snapshot(self) -> None:
        import src.jobs.delete_task_attachment_job as module

        original_engine = module.build_snapshot_engine
        original_storage = module.build_attachment_storage
        engine = _FakeEngine()
        storage = _FakeStorage()
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        module.build_attachment_storage = lambda _ctx: storage  # type: ignore[assignment]
        try:
            ctx = AppContext(cfg=SimpleNamespace(), deps={})
            cmd = Command(
                job_id="job-1",
                type="delete_task_attachment",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={"task_id": "task-1", "attachment_id": "a1", "deleted_by": "tester"},
            )
            result = DeleteTaskAttachmentJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original_engine  # type: ignore[assignment]
            module.build_attachment_storage = original_storage  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(engine.delete_calls, [("task-1", "a1")])
        self.assertEqual(storage.deleted_keys, ["attachments/test/task-1/a1-spec-final.docx"])
        self.assertEqual(engine.metadata_store.pending_calls[0]["deleted_by_user_id"], "tester")
        self.assertEqual(engine.metadata_store.deleted_calls[0]["attachment_id"], "a1")

    def test_delete_job_fails_when_attachment_is_missing(self) -> None:
        import src.jobs.delete_task_attachment_job as module

        original_engine = module.build_snapshot_engine
        module.build_snapshot_engine = lambda _ctx: _FakeEngine()  # type: ignore[assignment]
        try:
            ctx = AppContext(cfg=SimpleNamespace(), deps={})
            cmd = Command(
                job_id="job-2",
                type="delete_task_attachment",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={"task_id": "task-1", "attachment_id": "missing", "deleted_by": "tester"},
            )
            result = DeleteTaskAttachmentJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original_engine  # type: ignore[assignment]

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["code"], "attachment_not_found")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.jobs.delete_task_attachment_job import DeleteTaskAttachmentJob
from src.services.errors import TransientError


class _FakeMetadataStore:
    def __init__(self) -> None:
        self.pending_calls = []
        self.deleted_calls = []

    def get_by_attachment_id(self, attachment_id):  # noqa: ANN001
        if attachment_id != "a1":
            return None
        return (
            "task-1",
            SimpleNamespace(
                storage_key="attachments/test/task-1/a1-spec-final.docx",
                derived_preview_ref="attachments/test/task-1/a1/preview.pdf",
            ),
        )

    def mark_delete_pending(self, **kwargs):  # noqa: ANN001
        self.pending_calls.append(kwargs)

    def mark_deleted(self, **kwargs):  # noqa: ANN001
        self.deleted_calls.append(kwargs)


class _FakeEngine:
    def __init__(self) -> None:
        self.metadata_store = _FakeMetadataStore()
        self.delete_calls = []
        self.response_cache_store = _FakeResponseCacheStore()

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

    def get_response_cache_store(self):
        return self.response_cache_store


class _FakeStorage:
    def __init__(self) -> None:
        self.deleted_keys = []

    def delete_object(self, *, key):  # noqa: ANN001
        self.deleted_keys.append(key)


class _FakeResponseCacheStore:
    def __init__(self) -> None:
        self.deleted = []
        self.fail = False

    def delete(self, cache_key: str) -> None:
        if self.fail:
            raise TransientError("cache delete failed", code="s3_delete_failed")
        self.deleted.append(cache_key)


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
        self.assertEqual(
            storage.deleted_keys,
            ["attachments/test/task-1/a1-spec-final.docx", "attachments/test/task-1/a1/preview.pdf"],
        )
        self.assertEqual(engine.metadata_store.pending_calls[0]["deleted_by_user_id"], "tester")
        self.assertEqual(engine.metadata_store.deleted_calls[0]["attachment_id"], "a1")
        self.assertEqual(
            engine.response_cache_store.deleted,
            [
                "frontend_v2/default/api/masked",
                "frontend_v2/default/api/full",
                "frontend_v2/default/bff/masked",
                "frontend_v2/default/bff/full",
            ],
        )

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

    def test_delete_job_keeps_ok_when_cache_invalidation_fails(self) -> None:
        import src.jobs.delete_task_attachment_job as module

        original_engine = module.build_snapshot_engine
        original_storage = module.build_attachment_storage
        engine = _FakeEngine()
        engine.response_cache_store.fail = True
        storage = _FakeStorage()
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        module.build_attachment_storage = lambda _ctx: storage  # type: ignore[assignment]
        try:
            ctx = AppContext(cfg=SimpleNamespace(), deps={})
            cmd = Command(
                job_id="job-3",
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
        self.assertIn("frontend_response_cache_invalidation_failed", result["warnings"])


if __name__ == "__main__":
    unittest.main()

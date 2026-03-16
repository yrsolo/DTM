from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.services.errors import TransientError
from src.jobs.attach_task_file_job import AttachTaskFileJob


class _FakeResponseCacheStore:
    def __init__(self) -> None:
        self.deleted = []
        self.fail = False

    def delete(self, cache_key: str) -> None:
        if self.fail:
            raise TransientError("cache delete failed", code="s3_delete_failed")
        self.deleted.append(cache_key)


class _FakeEngine:
    def __init__(self) -> None:
        self.calls = []
        self.ready_calls = []
        self.preview_pending_calls = []
        self.preview_failed_calls = []
        self.response_cache_store = _FakeResponseCacheStore()

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

    def get_attachment_metadata_store(self):
        return self

    def get_by_attachment_id(self, attachment_id):  # noqa: ANN001
        return ("task-1", object()) if attachment_id else None

    def mark_ready(self, *, task_id, attachment_id):  # noqa: ANN001
        self.ready_calls.append((task_id, attachment_id))

    def mark_preview_pending(self, *, task_id, attachment_id):  # noqa: ANN001
        self.preview_pending_calls.append((task_id, attachment_id))

    def mark_preview_failed(self, *, task_id, attachment_id, error_code, error_message):  # noqa: ANN001
        self.preview_failed_calls.append((task_id, attachment_id, error_code, error_message))

    def get_response_cache_store(self):
        return self.response_cache_store


class _FakeProducer:
    def __init__(self) -> None:
        self.commands = []

    def send(self, cmd):  # noqa: ANN001
        self.commands.append(cmd)


class _FakeStatusStore:
    def __init__(self) -> None:
        self.queued = []

    def put_queued(self, cmd):  # noqa: ANN001
        self.queued.append(cmd)
        return SimpleNamespace(job_id=cmd.job_id, requested_at_utc=datetime.now(timezone.utc))


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
                    "key": "attachments/test/task-1/a1-file.docx",
                    "filename": "file.docx",
                    "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
        self.assertEqual(engine.calls[0][1].filename, "file.docx")
        self.assertEqual(engine.calls[0][1].kind, "docx")
        self.assertEqual(engine.ready_calls, [("task-1", engine.calls[0][1].attachment_id)])
        self.assertEqual(
            engine.response_cache_store.deleted,
            [
                "frontend_v2/default/api/masked",
                "frontend_v2/default/api/full",
                "frontend_v2/default/bff/masked",
                "frontend_v2/default/bff/full",
            ],
        )

    def test_attach_job_keeps_ok_when_cache_invalidation_fails(self) -> None:
        import src.jobs.attach_task_file_job as module

        original = module.build_snapshot_engine
        engine = _FakeEngine()
        engine.response_cache_store.fail = True
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        try:
            ctx = AppContext(cfg=SimpleNamespace(), deps={})
            cmd = Command(
                job_id="job-3",
                type="attach_task_file",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={
                    "task_id": "task-1",
                    "key": "attachments/test/task-1/a1-file.docx",
                    "filename": "file.docx",
                    "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "size": 123,
                    "uploaded_by": "tester",
                },
            )
            result = AttachTaskFileJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertIn("frontend_response_cache_invalidation_failed", result["warnings"])

    def test_attach_job_enqueues_doc_preview_when_configured(self) -> None:
        import src.jobs.attach_task_file_job as module

        original = module.build_snapshot_engine
        engine = _FakeEngine()
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        try:
            producer = _FakeProducer()
            status_store = _FakeStatusStore()
            ctx = AppContext(
                cfg=SimpleNamespace(),
                deps={
                    "doc_preview_converter": object(),
                    "command_queue_producer": producer,
                    "job_status_store": status_store,
                },
            )
            cmd = Command(
                job_id="job-4",
                type="attach_task_file",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={
                    "task_id": "task-1",
                    "key": "attachments/test/task-1/a1-file.doc",
                    "filename": "file.doc",
                    "mime": "application/msword",
                    "size": 123,
                    "uploaded_by": "tester",
                },
            )
            result = AttachTaskFileJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(producer.commands), 1)
        self.assertEqual(producer.commands[0].type, "generate_attachment_preview")
        self.assertEqual(engine.preview_pending_calls, [("task-1", engine.calls[0][1].attachment_id)])

    def test_attach_job_marks_doc_preview_failed_when_unconfigured(self) -> None:
        import src.jobs.attach_task_file_job as module

        original = module.build_snapshot_engine
        engine = _FakeEngine()
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        try:
            ctx = AppContext(cfg=SimpleNamespace(), deps={})
            cmd = Command(
                job_id="job-5",
                type="attach_task_file",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={
                    "task_id": "task-1",
                    "key": "attachments/test/task-1/a1-file.doc",
                    "filename": "file.doc",
                    "mime": "application/msword",
                    "size": 123,
                    "uploaded_by": "tester",
                },
            )
            result = AttachTaskFileJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(engine.preview_failed_calls), 1)

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
        self.assertEqual(result["error"]["code"], "mime_required")


if __name__ == "__main__":
    unittest.main()

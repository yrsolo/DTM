from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.contexts.attachments.internal.preview_job import GenerateAttachmentPreviewJob
from src.snapshot_engine.model import AttachmentMeta


class _FakeMetadataStore:
    def __init__(self, record: AttachmentMeta) -> None:
        self.record = record
        self.pending_calls = []
        self.ready_calls = []
        self.failed_calls = []

    def get_by_attachment_id(self, attachment_id):  # noqa: ANN001
        if attachment_id != self.record.attachment_id:
            return None
        return (self.record.task_id, self.record)

    def mark_preview_pending(self, *, task_id, attachment_id):  # noqa: ANN001
        self.pending_calls.append((task_id, attachment_id))

    def mark_preview_ready(self, *, task_id, attachment_id, derived_preview_ref):  # noqa: ANN001
        self.ready_calls.append((task_id, attachment_id, derived_preview_ref))

    def mark_preview_failed(self, *, task_id, attachment_id, error_code, error_message):  # noqa: ANN001
        self.failed_calls.append((task_id, attachment_id, error_code, error_message))


class _FakeEngine:
    def __init__(self, store: _FakeMetadataStore) -> None:
        self.store = store
        self.attach_calls = []
        self.response_cache_store = SimpleNamespace(delete=lambda _cache_key: None)

    def get_attachment_metadata_store(self):
        return self.store

    def attach_file_metadata(self, *, task_id, attachment):  # noqa: ANN001
        self.attach_calls.append((task_id, attachment))
        return {"artifact": "attach_task_file", "status": "ok"}

    def get_response_cache_store(self):
        return self.response_cache_store


class _FakeStorage:
    def generate_read_url(self, *, key, filename, download, expires_in_seconds=300):  # noqa: ANN001
        action = "download" if download else "view"
        return f"https://example.test/{action}/{key}"

    def generate_preview_upload_contract(self, *, key, mime_type="application/pdf", expires_in_seconds=900):  # noqa: ANN001
        return {"uploadUrl": f"https://example.test/upload/{key}", "headers": {}, "method": "PUT", "expiresIn": 900}


class _FakeConverter:
    def __init__(self, status="ready") -> None:
        self.calls = []
        self._status = status

    def convert_doc_to_pdf(self, **payload):  # noqa: ANN001
        self.calls.append(payload)
        return SimpleNamespace(
            status=self._status,
            attachment_id=payload.get("attachment_id"),
            preview_mime="application/pdf",
            preview_size_bytes=1234,
            error_code=None,
            error_message=None,
        )


class GenerateAttachmentPreviewJobTestCase(unittest.TestCase):
    def _make_record(self) -> AttachmentMeta:
        return AttachmentMeta(
            id="att-1",
            attachment_id="att-1",
            task_id="task-1",
            key="attachments/test/task-1/att-1-legacy.doc",
            storage_key="attachments/test/task-1/att-1-legacy.doc",
            filename="legacy.doc",
            filename_display="legacy.doc",
            filename_original="legacy.doc",
            mime="application/msword",
            mime_type="application/msword",
            kind="doc",
            size=10,
            size_bytes=10,
            uploaded_at_utc=datetime.now(timezone.utc),
            uploaded_by="tester",
            uploaded_by_user_id="tester",
            status="ready",
            snapshot_visible=True,
        )

    def test_generate_preview_success_marks_ready(self) -> None:
        import src.contexts.attachments.internal.preview_job as module

        record = self._make_record()
        store = _FakeMetadataStore(record)
        engine = _FakeEngine(store)
        converter = _FakeConverter()
        original_engine = module.build_snapshot_engine
        original_storage = module.build_attachment_storage
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        module.build_attachment_storage = lambda _ctx: _FakeStorage()  # type: ignore[assignment]
        try:
            ctx = AppContext(
                cfg=SimpleNamespace(runtime=SimpleNamespace(runtime=SimpleNamespace(env_default="test"))),
                deps={"doc_preview_converter": converter},
            )
            cmd = Command(
                job_id="job-preview-1",
                type="generate_attachment_preview",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={"task_id": "task-1", "attachment_id": "att-1"},
            )
            result = GenerateAttachmentPreviewJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original_engine  # type: ignore[assignment]
            module.build_attachment_storage = original_storage  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(store.pending_calls, [("task-1", "att-1")])
        self.assertEqual(len(store.ready_calls), 1)
        self.assertEqual(len(engine.attach_calls), 1)

    def test_generate_preview_fails_when_unconfigured(self) -> None:
        import src.contexts.attachments.internal.preview_job as module

        record = self._make_record()
        store = _FakeMetadataStore(record)
        engine = _FakeEngine(store)
        original_engine = module.build_snapshot_engine
        original_storage = module.build_attachment_storage
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        module.build_attachment_storage = lambda _ctx: _FakeStorage()  # type: ignore[assignment]
        try:
            ctx = AppContext(
                cfg=SimpleNamespace(runtime=SimpleNamespace(runtime=SimpleNamespace(env_default="test"))),
                deps={},
            )
            cmd = Command(
                job_id="job-preview-2",
                type="generate_attachment_preview",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="admin"),
                payload={"task_id": "task-1", "attachment_id": "att-1"},
            )
            result = GenerateAttachmentPreviewJob(ctx).run(cmd)
        finally:
            module.build_snapshot_engine = original_engine  # type: ignore[assignment]
            module.build_attachment_storage = original_storage  # type: ignore[assignment]

        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(store.failed_calls), 1)


if __name__ == "__main__":
    unittest.main()

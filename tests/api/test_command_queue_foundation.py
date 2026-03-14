from __future__ import annotations

import asyncio
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import index
from src.commands.model import Command, RequestedBy
from src.commands.serializer import command_from_json, command_to_json
from src.entrypoints.http.admin_task_attachments_handler import AdminTaskAttachmentsHandler
from src.entrypoints.http.admin_queue_handler import AdminQueueHandler
from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.job_status_handler import JobStatusHandler
from src.worker.model import JobStatusRecord


class _FakeProducer:
    def __init__(self) -> None:
        self.commands: list[Command] = []

    def send(self, cmd: Command) -> None:
        self.commands.append(cmd)


class _FakeStatusStore:
    def __init__(self) -> None:
        self.records: dict[str, JobStatusRecord] = {}

    def put_queued(self, cmd: Command) -> JobStatusRecord:
        record = JobStatusRecord(
            job_id=cmd.job_id,
            command_type=cmd.type,
            status="accepted",
            requested_at_utc=cmd.created_at_utc,
            requested_by={"source": cmd.requested_by.source},
        )
        self.records[cmd.job_id] = record
        return record

    def get(self, job_id: str) -> JobStatusRecord | None:
        return self.records.get(job_id)


class _FakeCtx:
    def __init__(self, producer=None, status_store=None) -> None:
        self.deps = {
            "command_queue_producer": producer,
            "job_status_store": status_store,
            "browser_auth_proxy_secret": "proxy-secret-test",
            "aws_access_key_id": "ak",
            "aws_secret_access_key": "sk",
        }
        self.cfg = SimpleNamespace(
            runtime=SimpleNamespace(
                runtime=SimpleNamespace(env_default="test"),
                triggers={"a1smsif4rc82qbj1e3hf": "morning", "trigger-1": "timer"},
                snapshot_engine=SimpleNamespace(bucket="dtm"),
                api={"auth_trusted_secret_header": "X-DTM-Proxy-Secret", "auth_trusted_fallback": "masked"},
            ),
            db=SimpleNamespace(object_storage={"endpoint_url_default": "https://storage.yandexcloud.net"}),
        )


class _FakeWorker:
    def __init__(self) -> None:
        self.messages = None

    async def run_once_from_messages(self, messages):
        self.messages = list(messages)
        return {"artifact": "command_worker", "status": "ok", "processed": len(self.messages)}


class _FakeAttachmentStore:
    def __init__(self) -> None:
        self.pending = {}
        self.lookup = {}

    def create_pending(self, **kwargs):
        attachment_id = kwargs["attachment_id"]
        record = SimpleNamespace(
            task_id=kwargs["task_id"],
            attachment_id=attachment_id,
            filename_display=kwargs["filename"],
            mime_type=kwargs["mime_type"],
            size_bytes=kwargs["size_bytes"],
            kind="docx",
            storage_key=kwargs["storage_key"],
            preview="",
        )
        self.pending[attachment_id] = record
        self.lookup[attachment_id] = (kwargs["task_id"], record)
        return record

    def get_by_attachment_id(self, attachment_id):
        return self.lookup.get(attachment_id)

    def mark_uploaded_unverified(self, *, task_id, attachment_id, storage_etag=None, storage_version=None):
        current = self.lookup[attachment_id][1]
        self.lookup[attachment_id] = (
            task_id,
            SimpleNamespace(
                **vars(current),
                storage_etag=storage_etag,
                storage_version=storage_version,
            ),
        )


class _FakeSnapshotEngine:
    def __init__(self) -> None:
        self._attachment_store = _FakeAttachmentStore()

    def get_prep_snapshot(self):
        return SimpleNamespace(tasks_by_id={"task-1": object()})

    def get_attachment_metadata_store(self):
        return self._attachment_store


class _FakeBoto3Client:
    def generate_presigned_url(self, *args, **kwargs):
        return "https://example.test/upload"

    def head_object(self, *args, **kwargs):
        return {
            "ContentLength": 128,
            "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "ETag": '"etag-1"',
            "VersionId": "v1",
        }


class _FakeBoto3Module:
    @staticmethod
    def client(*args, **kwargs):
        return _FakeBoto3Client()


class CommandQueueFoundationTestCase(unittest.TestCase):
    def test_command_serializer_roundtrip(self) -> None:
        command = Command(
            job_id="job-1",
            type="update_snapshot",
            created_at_utc=datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
            requested_by=RequestedBy(source="admin", user_id="u1"),
            payload={"force_refresh": True},
        )
        restored = command_from_json(command_to_json(command))
        self.assertEqual(restored.job_id, "job-1")
        self.assertEqual(restored.type, "update_snapshot")
        self.assertTrue(restored.payload["force_refresh"])
        self.assertEqual(restored.requested_by.source, "admin")

    def test_admin_queue_handler_returns_503_without_queue(self) -> None:
        handler = AdminQueueHandler(_FakeCtx())
        response = handler.handle(
            HttpRequest(method="POST", path="/admin/commands/update-snapshot", body={}, is_http_event=True)
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 503)

    def test_admin_queue_handler_enqueues_command(self) -> None:
        producer = _FakeProducer()
        status_store = _FakeStatusStore()
        handler = AdminQueueHandler(_FakeCtx(producer=producer, status_store=status_store))
        response = handler.handle(
            HttpRequest(
                method="POST",
                path="/admin/commands/send-reminders",
                body={"mode": "test", "force_test_chat": True},
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 202)
        self.assertEqual(len(producer.commands), 1)
        self.assertEqual(producer.commands[0].type, "send_reminders")
        payload = json.loads(response.body)
        self.assertEqual(payload["status"], "accepted")

    def test_admin_queue_handler_emulates_trigger_batch(self) -> None:
        producer = _FakeProducer()
        status_store = _FakeStatusStore()
        handler = AdminQueueHandler(_FakeCtx(producer=producer, status_store=status_store))
        response = handler.handle(
            HttpRequest(
                method="POST",
                path="/admin/commands/emulate-trigger",
                body={"trigger_id": "trigger-1"},
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 202)
        payload = json.loads(response.body)
        self.assertEqual(payload["artifact"], "command_batch_enqueued")
        self.assertEqual(payload["trigger_id"], "trigger-1")
        self.assertEqual(payload["trigger_mode"], "timer")
        self.assertEqual(payload["queued_count"], 3)
        self.assertEqual(
            [item["command_type"] for item in payload["commands"]],
            ["update_snapshot", "render_timeline_sheet", "render_designers_sheet"],
        )

    def test_admin_queue_handler_enqueues_attach_task_file_command(self) -> None:
        producer = _FakeProducer()
        status_store = _FakeStatusStore()
        handler = AdminQueueHandler(_FakeCtx(producer=producer, status_store=status_store))
        response = handler.handle(
            HttpRequest(
                method="POST",
                path="/admin/commands/attach-task-file",
                body={
                    "task_id": "task-1",
                    "key": "attachments/test/task-1/a1-file.docx",
                    "filename": "file.docx",
                    "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "size": 42,
                    "uploaded_by": "tester",
                },
                headers={
                    "X-DTM-Proxy-Secret": "proxy-secret-test",
                    "x-dtm-access-mode": "full",
                    "x-dtm-authenticated": "1",
                    "x-dtm-contour": "test",
                    "x-dtm-user-status": "approved",
                },
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 202)
        self.assertEqual(len(producer.commands), 1)
        self.assertEqual(producer.commands[0].type, "attach_task_file")
        self.assertEqual(producer.commands[0].payload["task_id"], "task-1")

    def test_admin_queue_handler_enqueues_cleanup_task_attachments_command(self) -> None:
        producer = _FakeProducer()
        status_store = _FakeStatusStore()
        handler = AdminQueueHandler(_FakeCtx(producer=producer, status_store=status_store))
        response = handler.handle(
            HttpRequest(
                method="POST",
                path="/admin/commands/cleanup-task-attachments",
                body={"ttl_seconds": 7200},
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 202)
        self.assertEqual(len(producer.commands), 1)
        self.assertEqual(producer.commands[0].type, "cleanup_task_attachments")
        self.assertEqual(producer.commands[0].payload["ttl_seconds"], 7200)

    def test_admin_queue_handler_returns_upload_contract_for_existing_task(self) -> None:
        import src.entrypoints.http.admin_task_attachments_handler as module

        original_build_snapshot_engine = module.build_snapshot_engine
        module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
        try:
            handler = AdminTaskAttachmentsHandler(_FakeCtx())
            with patch.dict(sys.modules, {"boto3": _FakeBoto3Module()}):
                response = handler.handle(
                    HttpRequest(
                        method="POST",
                        path="/admin/task-attachments/request-upload",
                        body={
                            "task_id": "task-1",
                            "filename": "spec final.docx",
                            "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "size": 128,
                            "uploaded_by": "tester",
                        },
                        headers={
                            "X-DTM-Proxy-Secret": "proxy-secret-test",
                            "x-dtm-access-mode": "full",
                            "x-dtm-authenticated": "1",
                            "x-dtm-contour": "test",
                            "x-dtm-user-status": "approved",
                        },
                        is_http_event=True,
                    )
                )
        finally:
            module.build_snapshot_engine = original_build_snapshot_engine  # type: ignore[assignment]
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 200)
        payload = json.loads(response.body)
        self.assertEqual(payload["artifact"], "attachment_upload_request")
        self.assertIn("attachments/test/task-1/", payload["key"])
        self.assertEqual(payload["headers"]["Content-Type"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertEqual(payload["kind"], "docx")

    def test_admin_task_attachments_handler_finalizes_and_enqueues_attach_command(self) -> None:
        import src.entrypoints.http.admin_task_attachments_handler as module

        original_build_snapshot_engine = module.build_snapshot_engine
        engine = _FakeSnapshotEngine()
        module.build_snapshot_engine = lambda _ctx: engine  # type: ignore[assignment]
        producer = _FakeProducer()
        status_store = _FakeStatusStore()
        try:
            handler = AdminTaskAttachmentsHandler(_FakeCtx(producer=producer, status_store=status_store))
            with patch.dict(sys.modules, {"boto3": _FakeBoto3Module()}):
                engine.get_attachment_metadata_store().lookup["a1"] = (
                    "task-1",
                    SimpleNamespace(
                        task_id="task-1",
                        attachment_id="a1",
                        storage_key="attachments/test/task-1/a1-spec-final.docx",
                        filename_display="spec final.docx",
                        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        size_bytes=128,
                        preview="",
                    ),
                )
                response = handler.handle(
                    HttpRequest(
                        method="POST",
                        path="/admin/task-attachments/finalize",
                        body={"task_id": "task-1", "attachment_id": "a1", "uploaded_by": "tester"},
                        headers={
                            "X-DTM-Proxy-Secret": "proxy-secret-test",
                            "x-dtm-access-mode": "full",
                            "x-dtm-authenticated": "1",
                            "x-dtm-contour": "test",
                            "x-dtm-user-status": "approved",
                        },
                        is_http_event=True,
                    )
                )
        finally:
            module.build_snapshot_engine = original_build_snapshot_engine  # type: ignore[assignment]
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 202)
        payload = json.loads(response.body)
        self.assertEqual(payload["artifact"], "attachment_finalize_enqueued")
        self.assertEqual(payload["task_id"], "task-1")
        self.assertEqual(payload["attachment_id"], "a1")
        self.assertEqual(len(producer.commands), 1)
        self.assertEqual(producer.commands[0].type, "attach_task_file")

    def test_admin_task_attachments_handler_enqueues_delete_command(self) -> None:
        producer = _FakeProducer()
        status_store = _FakeStatusStore()
        handler = AdminTaskAttachmentsHandler(_FakeCtx(producer=producer, status_store=status_store))
        response = handler.handle(
            HttpRequest(
                method="POST",
                path="/admin/task-attachments/delete",
                body={"task_id": "task-1", "attachment_id": "a1", "deleted_by": "tester"},
                headers={
                    "X-DTM-Proxy-Secret": "proxy-secret-test",
                    "x-dtm-access-mode": "full",
                    "x-dtm-authenticated": "1",
                    "x-dtm-contour": "test",
                    "x-dtm-user-status": "approved",
                },
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 202)
        self.assertEqual(len(producer.commands), 1)
        self.assertEqual(producer.commands[0].type, "delete_task_attachment")

    def test_job_status_handler_reads_status(self) -> None:
        status_store = _FakeStatusStore()
        cmd = Command(
            job_id="job-42",
            type="render_timeline_sheet",
            created_at_utc=datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
            requested_by=RequestedBy(source="admin"),
        )
        status_store.put_queued(cmd)
        handler = JobStatusHandler(_FakeCtx(status_store=status_store))
        response = handler.handle(HttpRequest(method="GET", path="/admin/jobs/job-42", is_http_event=True))
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 200)
        payload = json.loads(response.body)
        self.assertEqual(payload["job_id"], "job-42")
        self.assertEqual(payload["status"], "accepted")
        self.assertFalse(payload["retryable"])

    def test_index_routes_message_queue_event_to_worker(self) -> None:
        original_worker = index.APP_DEPS.get("command_worker")
        fake_worker = _FakeWorker()
        index.APP_DEPS["command_worker"] = fake_worker
        try:
            event = {
                "messages": [
                    {
                        "details": {
                            "message": {
                                "body": command_to_json(
                                    Command(
                                        job_id="job-7",
                                        type="update_snapshot",
                                        created_at_utc=datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
                                        requested_by=RequestedBy(source="trigger"),
                                    )
                                ),
                                "message_id": "m1",
                            }
                        }
                    }
                ]
            }
            response = asyncio.run(index.handler(event, None))
        finally:
            index.APP_DEPS["command_worker"] = original_worker
        self.assertEqual(response["statusCode"], 200)
        payload = json.loads(response["body"])
        self.assertEqual(payload["artifact"], "command_worker")
        self.assertEqual(payload["processed"], 1)
        self.assertEqual(len(fake_worker.messages), 1)

    def test_index_enqueues_trigger_event_when_queue_is_configured(self) -> None:
        original_producer = index.APP_DEPS.get("command_queue_producer")
        original_status_store = index.APP_DEPS.get("job_status_store")
        original_triggers = dict(index.APP_TRIGGERS)
        producer = _FakeProducer()
        status_store = _FakeStatusStore()
        index.APP_DEPS["command_queue_producer"] = producer
        index.APP_DEPS["job_status_store"] = status_store
        index.APP_TRIGGERS.clear()
        index.APP_TRIGGERS["trigger-1"] = "timer"
        try:
            event = {"messages": [{"details": {"trigger_id": "trigger-1"}}]}
            response = asyncio.run(index.handler(event, None))
        finally:
            index.APP_DEPS["command_queue_producer"] = original_producer
            index.APP_DEPS["job_status_store"] = original_status_store
            index.APP_TRIGGERS.clear()
            index.APP_TRIGGERS.update(original_triggers)
        self.assertEqual(response["statusCode"], 200)
        payload = json.loads(response["body"])
        self.assertEqual(payload["artifact"], "command_batch_enqueued")
        self.assertEqual(payload["command_type"], "update_snapshot")
        self.assertEqual(payload["queued_count"], 3)
        self.assertEqual(
            [item["command_type"] for item in payload["commands"]],
            ["update_snapshot", "render_timeline_sheet", "render_designers_sheet"],
        )
        self.assertEqual(len(producer.commands), 3)
        self.assertEqual(
            [cmd.type for cmd in producer.commands],
            ["update_snapshot", "render_timeline_sheet", "render_designers_sheet"],
        )


if __name__ == "__main__":
    unittest.main()

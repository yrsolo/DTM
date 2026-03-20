from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from uuid import uuid4

from src.commands.model import Command, RequestedBy
from src.commands.types import (
    ATTACH_TASK_FILE,
    CLEANUP_TASK_ATTACHMENTS,
    RENDER_DESIGNERS_SHEET,
    RENDER_TIMELINE_SHEET,
    SEND_REMINDERS,
    UPDATE_SNAPSHOT,
)
from src.contexts.snapshot.public import (
    get_prep_snapshot as _get_prep_snapshot,
)
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response, json_response
from src.platform.runtime.command_runtime import get_command_runtime
from src.entrypoints.triggers.trigger_plan import planned_trigger_commands, resolve_trigger_mode_by_id


def get_prep_snapshot(ctx):
    return _get_prep_snapshot(ctx)


class AdminQueueHandler:
    def __init__(self, ctx) -> None:
        self._ctx = ctx

    def _command_runtime(self):
        return get_command_runtime(self._ctx)

    @staticmethod
    def _requested_by(req: HttpRequest) -> RequestedBy:
        headers = dict(req.headers or {})
        return RequestedBy(
            source="admin",
            user_id=str(headers.get("X-User-Id", "")).strip() or None,
            chat_id=str(headers.get("X-Chat-Id", "")).strip() or None,
        )

    def _enqueue(self, *, command_type: str, payload: dict, req: HttpRequest) -> HttpResponse:
        command_runtime = self._command_runtime()
        if not command_runtime.can_enqueue():
            return error_response(
                503,
                code="queue_unavailable",
                message="Command queue is not configured for current environment.",
            )
        cmd = Command(
            job_id=uuid4().hex,
            type=command_type,
            created_at_utc=datetime.now(timezone.utc),
            requested_by=self._requested_by(req),
            payload=dict(payload),
        )
        record = command_runtime.enqueue(cmd)
        return json_response(
            202,
            {
                "artifact": "command_enqueued",
                "status": "accepted",
                "job_id": cmd.job_id,
                "command_type": cmd.type,
                "queued_at": record.requested_at_utc.isoformat(),
            },
        )

    def _enqueue_batch(self, *, planned: list[tuple[str, dict]], req: HttpRequest, artifact: str) -> HttpResponse:
        command_runtime = self._command_runtime()
        if not command_runtime.can_enqueue():
            return error_response(
                503,
                code="queue_unavailable",
                message="Command queue is not configured for current environment.",
            )
        commands = []
        for command_type, payload in planned:
            cmd = Command(
                job_id=uuid4().hex,
                type=command_type,
                created_at_utc=datetime.now(timezone.utc),
                requested_by=self._requested_by(req),
                payload=dict(payload),
            )
            record = command_runtime.enqueue(cmd)
            commands.append(
                {
                    "job_id": cmd.job_id,
                    "command_type": cmd.type,
                    "queued_at": record.requested_at_utc.isoformat(),
                    "payload": dict(cmd.payload),
                }
            )
        return json_response(
            202,
            {
                "artifact": artifact,
                "status": "accepted",
                "queued_count": len(commands),
                "commands": commands,
                "job_id": commands[0]["job_id"],
                "command_type": commands[0]["command_type"],
            },
        )

    @staticmethod
    def _safe_filename(name: str) -> str:
        text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(name or "").strip())
        return text.strip("-") or "file.bin"

    def _request_upload(self, *, body: dict, req: HttpRequest) -> HttpResponse:
        task_id = str(body.get("task_id", "")).strip()
        filename = str(body.get("filename", "")).strip()
        mime = str(body.get("mime", "")).strip() or "application/octet-stream"
        try:
            size = max(int(body.get("size", 0) or 0), 0)
        except (TypeError, ValueError):
            return error_response(400, code="size_invalid", message="size must be an integer.")
        if not task_id:
            return error_response(400, code="task_id_required", message="task_id is required.")
        if not filename:
            return error_response(400, code="filename_required", message="filename is required.")
        try:
            prep = get_prep_snapshot(self._ctx)
        except Exception as error:
            return error_response(
                503,
                code="snapshot_unavailable",
                message="Snapshot engine is temporarily unavailable.",
                details={"errorType": type(error).__name__},
            )
        if prep is None or task_id not in prep.tasks_by_id:
            return error_response(404, code="task_not_found", message="Task was not found in current snapshot.")
        try:
            import boto3  # type: ignore
        except Exception:
            return error_response(503, code="s3_sdk_missing", message="Upload contract is unavailable.")
        env_name = str(self._ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev"
        bucket = str(self._ctx.cfg.runtime.snapshot_engine.bucket or "").strip()
        endpoint_url = str(self._ctx.cfg.db.object_storage.get("endpoint_url_default", "")).strip() or None
        attachment_id = str(body.get("attachment_id", "")).strip() or uuid4().hex
        safe_filename = self._safe_filename(filename)
        object_key = f"attachments/{env_name}/{task_id}/{attachment_id}-{safe_filename}"
        client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=self._ctx.deps.get("aws_access_key_id"),
            aws_secret_access_key=self._ctx.deps.get("aws_secret_access_key"),
        )
        upload_url = client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": object_key, "ContentType": mime},
            ExpiresIn=900,
            HttpMethod="PUT",
        )
        return json_response(
            200,
            {
                "artifact": "attachment_upload_request",
                "status": "ok",
                "task_id": task_id,
                "attachment_id": attachment_id,
                "key": object_key,
                "filename": filename,
                "mime": mime,
                "size": size,
                "expiresIn": 900,
                "method": "PUT",
                "uploadUrl": upload_url,
                "headers": {"Content-Type": mime},
                "requestedBy": {
                    "source": self._requested_by(req).source,
                    "user_id": self._requested_by(req).user_id,
                    "chat_id": self._requested_by(req).chat_id,
                },
            },
        )

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        if str(req.method or "").strip().upper() != "POST":
            return None
        path = normalize_path(req.path)
        body = dict(req.body or {})
        if path == "/admin/attachments/request-upload":
            return self._request_upload(body=body, req=req)
        if path == "/admin/commands/update-snapshot":
            return self._enqueue(
                command_type=UPDATE_SNAPSHOT,
                payload={"force_refresh": bool(body.get("force_refresh", True)), "dry_run": bool(body.get("dry_run", False))},
                req=req,
            )
        if path == "/admin/commands/render-timeline":
            return self._enqueue(
                command_type=RENDER_TIMELINE_SHEET,
                payload={"statuses": list(body.get("statuses", ["work", "pre_done"])), "dry_run": bool(body.get("dry_run", False))},
                req=req,
            )
        if path == "/admin/commands/render-designers":
            return self._enqueue(
                command_type=RENDER_DESIGNERS_SHEET,
                payload={"statuses": list(body.get("statuses", ["work", "pre_done"])), "dry_run": bool(body.get("dry_run", False))},
                req=req,
            )
        if path == "/admin/commands/send-reminders":
            return self._enqueue(
                command_type=SEND_REMINDERS,
                payload={
                    "mode": str(body.get("mode", "morning")).strip().lower() or "morning",
                    "statuses": list(body.get("statuses", ["work", "pre_done"])),
                    "include_today": bool(body.get("include_today", True)),
                    "include_next_workday": bool(body.get("include_next_workday", True)),
                    "force_test_chat": bool(body.get("force_test_chat", False)),
                    "mock_external": bool(body.get("mock_external", False)),
                },
                req=req,
            )
        if path == "/admin/commands/emulate-trigger":
            trigger_id = str(body.get("trigger_id", "")).strip()
            trigger_mode = resolve_trigger_mode_by_id(trigger_id, dict(self._ctx.cfg.runtime.triggers))
            if not trigger_id:
                return error_response(400, code="trigger_id_required", message="trigger_id is required.")
            if not trigger_mode:
                return error_response(
                    404,
                    code="trigger_not_found",
                    message="Trigger id is not configured in runtime.triggers.",
                    details={"trigger_id": trigger_id},
                )
            planned = planned_trigger_commands(trigger_mode)
            if not planned:
                return error_response(
                    400,
                    code="trigger_mode_unsupported",
                    message="Configured trigger mode cannot be emulated through queue intake.",
                    details={"trigger_id": trigger_id, "trigger_mode": trigger_mode},
                )
            response = self._enqueue_batch(
                planned=planned,
                req=req,
                artifact="command_batch_enqueued" if len(planned) > 1 else "command_enqueued",
            )
            payload = json.loads(response.body)
            payload["trigger_id"] = trigger_id
            payload["trigger_mode"] = trigger_mode
            return json_response(response.status, payload)
        if path == "/admin/commands/attach-task-file":
            return self._enqueue(
                command_type=ATTACH_TASK_FILE,
                payload={
                    "task_id": str(body.get("task_id", "")).strip(),
                    "attachment_id": str(body.get("attachment_id", "")).strip(),
                    "key": str(body.get("key", "")).strip(),
                    "filename": str(body.get("filename", "")).strip(),
                    "mime": str(body.get("mime", "")).strip(),
                    "size": body.get("size", 0),
                    "uploaded_by": str(body.get("uploaded_by", "")).strip(),
                    "preview": str(body.get("preview", "")).strip(),
                },
                req=req,
            )
        if path == "/admin/commands/cleanup-task-attachments":
            ttl_seconds = body.get("ttl_seconds", 86400)
            try:
                ttl_seconds = int(ttl_seconds)
            except (TypeError, ValueError):
                return error_response(400, code="ttl_seconds_invalid", message="ttl_seconds must be an integer.")
            if ttl_seconds <= 0:
                return error_response(400, code="ttl_seconds_invalid", message="ttl_seconds must be positive.")
            return self._enqueue(
                command_type=CLEANUP_TASK_ATTACHMENTS,
                payload={"ttl_seconds": ttl_seconds},
                req=req,
            )
        return None

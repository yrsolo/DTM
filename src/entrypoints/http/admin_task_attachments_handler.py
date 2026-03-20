from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.parse import urlsplit
from uuid import uuid4

from src.commands.model import Command, RequestedBy
from src.commands.types import ATTACH_TASK_FILE, DELETE_TASK_ATTACHMENT
from src.contexts.attachments.public import (
    get_attachment_finalize_service,
    get_attachment_snapshot_capability,
    get_attachment_storage,
)
from src.entrypoints.http.access_context import resolve_access_context
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response, json_response, path_matches
from src.platform.runtime.command_runtime import get_command_runtime
from src.services.errors import AppError

get_snapshot_capability = get_attachment_snapshot_capability
get_attachment_storage_capability = get_attachment_storage
get_attachment_finalize_capability = get_attachment_finalize_service


class AdminTaskAttachmentsHandler:
    def __init__(self, ctx) -> None:
        self._ctx = ctx

    def _command_runtime(self):
        return get_command_runtime(self._ctx)

    @staticmethod
    def _upload_error_details(
        *,
        reason: str,
        task_id: str,
        filename: str,
        mime: str,
        size: int | str | None,
        uploaded_by: str,
        extra: dict[str, object] | None = None,
    ) -> dict[str, object]:
        details: dict[str, object] = {
            "artifact": "attachment_upload_request_error",
            "step": "request-upload",
            "reason": reason,
            "task_id": task_id,
            "filename": filename,
            "mime": mime,
            "size": size,
            "uploaded_by_present": bool(str(uploaded_by or "").strip()),
        }
        if extra:
            details.update(extra)
        return details

    @staticmethod
    def _requested_by(req: HttpRequest) -> RequestedBy:
        headers = dict(req.headers or {})
        return RequestedBy(
            source="admin",
            user_id=str(headers.get("X-User-Id", "")).strip() or None,
            chat_id=str(headers.get("X-Chat-Id", "")).strip() or None,
        )

    def _require_admin_access(self, req: HttpRequest) -> HttpResponse | None:
        access = resolve_access_context(self._ctx, req)
        if bool(access.trusted_ingress) and bool(access.authenticated) and str(access.mode) == "full" and str(access.user_status or "") == "approved":
            return None
        return error_response(403, code="forbidden", message="Forbidden.", details={"reason": "attachment_admin_forbidden"})

    def _enqueue(self, *, command_type: str, payload: dict, req: HttpRequest, artifact: str) -> HttpResponse:
        command_runtime = self._command_runtime()
        if not command_runtime.can_enqueue():
            return error_response(503, code="queue_unavailable", message="Command queue is not configured for current environment.")
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
                "artifact": artifact,
                "status": "accepted",
                "job_id": cmd.job_id,
                "command_type": cmd.type,
                "queued_at": record.requested_at_utc.isoformat(),
            },
        )

    def _request_upload(self, *, body: dict, req: HttpRequest) -> HttpResponse:
        denied = self._require_admin_access(req)
        if denied is not None:
            return denied
        task_id = str(body.get("task_id", "")).strip()
        filename = str(body.get("filename", "")).strip()
        mime = str(body.get("mime", "")).strip()
        uploaded_by = str(body.get("uploaded_by", "")).strip() or str((req.headers or {}).get("X-User-Id", "")).strip()
        try:
            size = max(int(body.get("size", 0) or 0), 0)
        except (TypeError, ValueError):
            return error_response(
                400,
                code="size_invalid",
                message="size must be an integer.",
                details=self._upload_error_details(
                    reason="size_invalid",
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=body.get("size"),
                    uploaded_by=uploaded_by,
                ),
            )
        if not task_id:
            return error_response(
                400,
                code="task_id_required",
                message="task_id is required.",
                details=self._upload_error_details(
                    reason="task_id_required",
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=size,
                    uploaded_by=uploaded_by,
                    extra={"field": "task_id"},
                ),
            )
        if not filename:
            return error_response(
                400,
                code="filename_required",
                message="filename is required.",
                details=self._upload_error_details(
                    reason="filename_required",
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=size,
                    uploaded_by=uploaded_by,
                    extra={"field": "filename"},
                ),
            )
        if not mime:
            return error_response(
                400,
                code="mime_required",
                message="mime is required.",
                details=self._upload_error_details(
                    reason="mime_required",
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=size,
                    uploaded_by=uploaded_by,
                    extra={"field": "mime"},
                ),
            )
        if not uploaded_by:
            return error_response(
                400,
                code="uploaded_by_required",
                message="uploaded_by is required.",
                details=self._upload_error_details(
                    reason="uploaded_by_required",
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=size,
                    uploaded_by=uploaded_by,
                    extra={"field": "uploaded_by"},
                ),
            )
        try:
            engine = get_snapshot_capability(self._ctx)
            prep = engine.get_prep_snapshot()
        except Exception as error:
            return error_response(
                503,
                code="snapshot_unavailable",
                message="Snapshot engine is temporarily unavailable.",
                details=self._upload_error_details(
                    reason="snapshot_unavailable",
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=size,
                    uploaded_by=uploaded_by,
                    extra={"errorType": type(error).__name__},
                ),
            )
        if prep is None or task_id not in prep.tasks_by_id:
            return error_response(
                404,
                code="task_not_found",
                message="Task was not found in current snapshot.",
                details=self._upload_error_details(
                    reason="task_not_found",
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=size,
                    uploaded_by=uploaded_by,
                ),
            )
        attachment_id = str(body.get("attachment_id", "")).strip() or uuid4().hex
        storage = get_attachment_storage_capability(self._ctx)
        object_key = storage.build_object_key(
            env_name=str(self._ctx.cfg.runtime.runtime.env_default or ""),
            task_id=task_id,
            attachment_id=attachment_id,
            filename=filename,
        )
        try:
            record = engine.get_attachment_metadata_store().create_pending(
                task_id=task_id,
                attachment_id=attachment_id,
                filename=filename,
                mime_type=mime,
                size_bytes=size,
                storage_key=object_key,
                uploaded_by_user_id=uploaded_by,
            )
            contract = storage.generate_upload_contract(key=object_key, mime_type=record.mime_type)
        except AppError as error:
            return error_response(
                400 if error.code.endswith("_unsupported") or error.code.endswith("_required") else 503,
                code=error.code,
                message=str(error),
                details=self._upload_error_details(
                    reason=error.code,
                    task_id=task_id,
                    filename=filename,
                    mime=mime,
                    size=size,
                    uploaded_by=uploaded_by,
                ),
            )
        upload_url = str(contract["uploadUrl"])
        parsed_upload_url = urlsplit(upload_url)
        expires_in = int(contract["expiresIn"])
        expires_at = datetime.now(timezone.utc).timestamp() + expires_in
        payload = {
            "artifact": "attachment_upload_request",
            "status": "ok",
            "task_id": task_id,
            "attachment_id": attachment_id,
            "filename": filename,
            "mime": record.mime_type,
            "size": size,
            "kind": record.kind,
            "key": object_key,
            "method": contract["method"],
            "uploadUrl": upload_url,
            "headers": contract["headers"],
            "expiresIn": expires_in,
            "diagnostics": {
                "uploadContractVersion": "presigned_put_v1",
                "signedMethod": str(contract["method"]),
                "signedContentType": record.mime_type,
                "requiredHeaders": dict(contract["headers"] or {}),
                "uploadUrlScheme": str(parsed_upload_url.scheme or ""),
                "uploadUrlHost": str(parsed_upload_url.netloc or ""),
                "uploadUrlPath": str(parsed_upload_url.path or ""),
                "expiresAtUtc": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
                "browserMayRequirePreflight": True,
                "notes": [
                    "Use the returned uploadUrl exactly as-is.",
                    "Send a direct PUT request with the exact Content-Type from headers.",
                    "Browser uploads may require successful OPTIONS/CORS handling on the storage ingress.",
                ],
            },
        }
        return json_response(200, payload)

    def _finalize(self, *, body: dict, req: HttpRequest) -> HttpResponse:
        denied = self._require_admin_access(req)
        if denied is not None:
            return denied
        task_id = str(body.get("task_id", "")).strip()
        attachment_id = str(body.get("attachment_id", "")).strip()
        uploaded_by = str(body.get("uploaded_by", "")).strip() or str((req.headers or {}).get("X-User-Id", "")).strip()
        if not task_id:
            return error_response(400, code="task_id_required", message="task_id is required.")
        if not attachment_id:
            return error_response(400, code="attachment_id_required", message="attachment_id is required.")
        if not uploaded_by:
            return error_response(400, code="uploaded_by_required", message="uploaded_by is required.")
        try:
            engine = get_snapshot_capability(self._ctx)
            finalize = get_attachment_finalize_capability(self._ctx)
            verified = finalize.finalize(task_id=task_id, attachment_id=attachment_id)
            lookup = engine.get_attachment_metadata_store().get_by_attachment_id(attachment_id)
            if lookup is None:
                return error_response(404, code="attachment_not_found", message="Attachment was not found.")
            _task_id, record = lookup
        except AppError as error:
            return error_response(400 if error.code.startswith("attachment_") else 503, code=error.code, message=str(error))
        response = self._enqueue(
            command_type=ATTACH_TASK_FILE,
            payload={
                "task_id": task_id,
                "attachment_id": attachment_id,
                "key": record.storage_key,
                "filename": record.filename_display,
                "mime": record.mime_type,
                "size": record.size_bytes,
                "uploaded_by": uploaded_by,
                "preview": record.preview,
            },
            req=req,
            artifact="attachment_finalize_enqueued",
        )
        if response.status != 202:
            return response
        payload = dict(json.loads(response.body))
        payload["verified"] = {
            "mime": verified.mime_type,
            "size": verified.content_length,
            "etag": verified.storage_etag,
            "version": verified.storage_version,
        }
        payload["attachment_id"] = attachment_id
        payload["task_id"] = task_id
        return json_response(202, payload)

    def _delete(self, *, body: dict, req: HttpRequest) -> HttpResponse:
        denied = self._require_admin_access(req)
        if denied is not None:
            return denied
        task_id = str(body.get("task_id", "")).strip()
        attachment_id = str(body.get("attachment_id", "")).strip()
        deleted_by = str(body.get("deleted_by", "")).strip() or str((req.headers or {}).get("X-User-Id", "")).strip()
        if not task_id:
            return error_response(400, code="task_id_required", message="task_id is required.")
        if not attachment_id:
            return error_response(400, code="attachment_id_required", message="attachment_id is required.")
        if not deleted_by:
            return error_response(400, code="deleted_by_required", message="deleted_by is required.")
        return self._enqueue(
            command_type=DELETE_TASK_ATTACHMENT,
            payload={"task_id": task_id, "attachment_id": attachment_id, "deleted_by": deleted_by},
            req=req,
            artifact="attachment_delete_enqueued",
        )

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        method = str(req.method or "").strip().upper()
        path = normalize_path(req.path)
        request_upload_paths = {
            "/ops/admin/task-attachments/request-upload",
            "/test/ops/admin/task-attachments/request-upload",
            "/admin/task-attachments/request-upload",
            "/admin/attachments/request-upload",
        }
        finalize_paths = {
            "/ops/admin/task-attachments/finalize",
            "/test/ops/admin/task-attachments/finalize",
            "/admin/task-attachments/finalize",
        }
        delete_paths = {
            "/ops/admin/task-attachments/delete",
            "/test/ops/admin/task-attachments/delete",
            "/admin/task-attachments/delete",
        }
        legacy_attach_paths = {
            "/admin/commands/attach-task-file",
        }
        if method == "POST" and path_matches(path, request_upload_paths, normalize_path):
            return self._request_upload(body=dict(req.body or {}), req=req)
        if method == "POST" and path_matches(path, finalize_paths, normalize_path):
            return self._finalize(body=dict(req.body or {}), req=req)
        if method == "POST" and path_matches(path, delete_paths, normalize_path):
            return self._delete(body=dict(req.body or {}), req=req)
        if method == "POST" and path_matches(path, legacy_attach_paths, normalize_path):
            body = dict(req.body or {})
            denied = self._require_admin_access(req)
            if denied is not None:
                return denied
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
                artifact="command_enqueued",
            )
        return None

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.platform.context import AppContext
from src.platform.runtime.commands.model import Command
from src.platform.runtime.commands.types import GENERATE_ATTACHMENT_PREVIEW
from src.contexts.attachments.contracts import (
    ATTACHMENT_STATUS_READY,
    build_attachment_capabilities,
    infer_attachment_kind,
)
from src.contexts.attachments.public import (
    get_attachment_snapshot_api,
    get_attachment_storage,
    get_doc_preview_converter,
)
from src.contexts.snapshot.contracts import AttachmentMeta
from src.platform.runtime.command_runtime import get_command_runtime
from src.platform.runtime.frontend_cache_invalidation import invalidate_default_frontend_cache_store
from src.platform.errors import AppError, TransientError, UserError

get_snapshot_attachment_api = get_attachment_snapshot_api
get_attachment_storage_capability = get_attachment_storage


class AttachTaskFileJob:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    @staticmethod
    def _require_text(payload: dict, key: str) -> str:
        value = str(payload.get(key, "")).strip()
        if not value:
            raise UserError(f"{key} is required", code=f"{key}_required")
        return value

    @staticmethod
    def _parse_size(payload: dict) -> int:
        raw = payload.get("size", 0)
        try:
            return max(int(raw or 0), 0)
        except (TypeError, ValueError) as error:
            raise UserError("size must be an integer", code="size_invalid") from error

    def run(self, cmd):
        payload = dict(cmd.payload or {})
        try:
            task_id = self._require_text(payload, "task_id")
            attachment_id = str(payload.get("attachment_id", "")).strip() or uuid4().hex
            mime_type = self._require_text(payload, "mime")
            size_bytes = self._parse_size(payload)
            kind = infer_attachment_kind(mime_type)
            doc_preview_state = "none"
            command_runtime = get_command_runtime(self._ctx)
            converter_configured = get_doc_preview_converter(self._ctx) is not None
            preview_queue_available = command_runtime.can_enqueue()
            preview_enabled = converter_configured and preview_queue_available
            if kind == "doc":
                doc_preview_state = "pending" if preview_enabled else "failed"
            attachment = AttachmentMeta(
                id=attachment_id,
                attachment_id=attachment_id,
                task_id=task_id,
                key=self._require_text(payload, "key"),
                storage_key=self._require_text(payload, "key"),
                filename=self._require_text(payload, "filename"),
                filename_original=self._require_text(payload, "filename"),
                filename_display=self._require_text(payload, "filename"),
                mime=mime_type,
                mime_type=mime_type,
                kind=kind,
                size=size_bytes,
                size_bytes=size_bytes,
                uploaded_at_utc=datetime.now(timezone.utc),
                uploaded_by=self._require_text(payload, "uploaded_by"),
                uploaded_by_user_id=self._require_text(payload, "uploaded_by"),
                preview=str(payload.get("preview", "")).strip(),
                preview_capabilities=build_attachment_capabilities(kind),
                status=ATTACHMENT_STATUS_READY,
                snapshot_visible=True,
                preview_state=doc_preview_state,
            )
            snapshot_attachments = get_snapshot_attachment_api(self._ctx)
            metadata_store = snapshot_attachments.get_attachment_metadata_store()
            lookup = metadata_store.get_by_attachment_id(attachment_id)
            if lookup is not None:
                metadata_store.mark_ready(task_id=task_id, attachment_id=attachment_id)
                if kind == "doc":
                    if preview_enabled:
                        metadata_store.mark_preview_pending(task_id=task_id, attachment_id=attachment_id)
                    else:
                        error_code = (
                            "doc_preview_converter_unconfigured"
                            if not converter_configured
                            else "doc_preview_queue_unavailable"
                        )
                        metadata_store.mark_preview_failed(
                            task_id=task_id,
                            attachment_id=attachment_id,
                            error_code=error_code,
                            error_message="Doc preview pipeline is unavailable.",
                        )
            result = snapshot_attachments.attach_file_metadata(task_id=task_id, attachment=attachment)
            if kind == "doc":
                if preview_enabled:
                    preview_cmd = Command(
                        job_id=uuid4().hex,
                        type=GENERATE_ATTACHMENT_PREVIEW,
                        created_at_utc=datetime.now(timezone.utc),
                        requested_by=cmd.requested_by,
                        payload={"task_id": task_id, "attachment_id": attachment_id},
                    )
                    command_runtime.enqueue(preview_cmd)
                    result["preview_job_id"] = preview_cmd.job_id
                else:
                    result["warnings"] = list(result.get("warnings", []) or [])
                    if not converter_configured:
                        result["warnings"].append("doc_preview_converter_unconfigured")
                    elif not preview_queue_available:
                        result["warnings"].append("doc_preview_queue_unavailable")
            try:
                invalidate_default_frontend_cache_store(snapshot_attachments.get_response_cache_store())
            except AppError:
                result["warnings"] = list(result.get("warnings", []) or [])
                result["warnings"].append("frontend_response_cache_invalidation_failed")
            result["object_key"] = attachment.key
            return result
        except AppError as error:
            return {
                "artifact": "attach_task_file",
                "status": "failed",
                "error": {"code": error.code, "message": str(error)},
            }


class DeleteTaskAttachmentJob:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    @staticmethod
    def _require_text(payload: dict, key: str) -> str:
        value = str(payload.get(key, "")).strip()
        if not value:
            raise UserError(f"{key} is required", code=f"{key}_required")
        return value

    def run(self, cmd):
        payload = dict(cmd.payload or {})
        try:
            task_id = self._require_text(payload, "task_id")
            attachment_id = self._require_text(payload, "attachment_id")
            deleted_by = self._require_text(payload, "deleted_by")
            snapshot_attachments = get_snapshot_attachment_api(self._ctx)
            metadata_store = snapshot_attachments.get_attachment_metadata_store()
            lookup = metadata_store.get_by_attachment_id(attachment_id)
            if lookup is None or lookup[0] != task_id:
                raise UserError("Attachment was not found.", code="attachment_not_found")
            _task_id, record = lookup
            metadata_store.mark_delete_pending(
                task_id=task_id,
                attachment_id=attachment_id,
                deleted_by_user_id=deleted_by,
            )
            delete_warning = ""
            try:
                    get_attachment_storage_capability(self._ctx).delete_object(key=record.storage_key)
            except AppError as error:
                delete_warning = error.code
            preview_warning = ""
            preview_key = str(getattr(record, "derived_preview_ref", "") or "").strip()
            if preview_key:
                try:
                    get_attachment_storage_capability(self._ctx).delete_object(key=preview_key)
                except AppError as error:
                    preview_warning = error.code
            metadata_store.mark_deleted(
                task_id=task_id,
                attachment_id=attachment_id,
                deleted_by_user_id=deleted_by,
                warning=delete_warning or preview_warning,
            )
            result = snapshot_attachments.delete_attachment(task_id=task_id, attachment_id=attachment_id)
            try:
                invalidate_default_frontend_cache_store(snapshot_attachments.get_response_cache_store())
            except AppError:
                result["warnings"] = list(result.get("warnings", []) or [])
                result["warnings"].append("frontend_response_cache_invalidation_failed")
            if delete_warning:
                result["warnings"] = [delete_warning]
            if preview_warning:
                result["warnings"] = list(result.get("warnings", []) or [])
                result["warnings"].append(preview_warning)
            return result
        except AppError as error:
            return {
                "artifact": "delete_task_attachment",
                "status": "failed",
                "error": {"code": error.code, "message": str(error)},
            }


class CleanupTaskAttachmentsJob:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    @staticmethod
    def _parse_ttl_seconds(payload: dict) -> int:
        raw = payload.get("ttl_seconds", 86400)
        try:
            ttl_seconds = int(raw)
        except (TypeError, ValueError) as error:
            raise UserError("ttl_seconds must be an integer", code="ttl_seconds_invalid") from error
        if ttl_seconds <= 0:
            raise UserError("ttl_seconds must be positive", code="ttl_seconds_invalid")
        return ttl_seconds

    def run(self, cmd):
        payload = dict(cmd.payload or {})
        try:
            ttl_seconds = self._parse_ttl_seconds(payload)
            snapshot_attachments = get_snapshot_attachment_api(self._ctx)
            storage = get_attachment_storage_capability(self._ctx)
            result = snapshot_attachments.cleanup_stale_attachments(
                ttl_seconds=ttl_seconds,
                delete_object=storage.delete_object,
            )
            result["ttl_seconds"] = ttl_seconds
            return result
        except AppError as error:
            return {
                "artifact": "cleanup_task_attachments",
                "status": "failed",
                "error": {"code": error.code, "message": str(error)},
            }


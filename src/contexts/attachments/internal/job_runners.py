from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.app.context import AppContext
from src.commands.model import Command
from src.commands.types import GENERATE_ATTACHMENT_PREVIEW
from src.contexts.attachments.contracts import (
    ATTACHMENT_STATUS_READY,
    build_attachment_capabilities,
    infer_attachment_kind,
)
from src.contexts.attachments.public import get_attachment_snapshot_capability, get_attachment_storage
from src.contexts.snapshot.contracts import AttachmentMeta
from src.platform.runtime.frontend_cache_invalidation import invalidate_default_frontend_cache_store
from src.services.errors import AppError, TransientError, UserError

build_snapshot_engine = get_attachment_snapshot_capability
build_attachment_storage = get_attachment_storage


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
            producer = self._ctx.deps.get("command_queue_producer")
            status_store = self._ctx.deps.get("job_status_store")
            converter_configured = self._ctx.deps.get("doc_preview_converter") is not None
            preview_queue_available = producer is not None and status_store is not None
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
            engine = build_snapshot_engine(self._ctx)
            metadata_store = engine.get_attachment_metadata_store()
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
            result = engine.attach_file_metadata(task_id=task_id, attachment=attachment)
            if kind == "doc":
                if preview_enabled:
                    preview_cmd = Command(
                        job_id=uuid4().hex,
                        type=GENERATE_ATTACHMENT_PREVIEW,
                        created_at_utc=datetime.now(timezone.utc),
                        requested_by=cmd.requested_by,
                        payload={"task_id": task_id, "attachment_id": attachment_id},
                    )
                    producer.send(preview_cmd)
                    status_store.put_queued(preview_cmd)
                    result["preview_job_id"] = preview_cmd.job_id
                else:
                    result["warnings"] = list(result.get("warnings", []) or [])
                    if not converter_configured:
                        result["warnings"].append("doc_preview_converter_unconfigured")
                    elif not preview_queue_available:
                        result["warnings"].append("doc_preview_queue_unavailable")
            try:
                invalidate_default_frontend_cache_store(engine.get_response_cache_store())
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
            engine = build_snapshot_engine(self._ctx)
            metadata_store = engine.get_attachment_metadata_store()
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
                build_attachment_storage(self._ctx).delete_object(key=record.storage_key)
            except AppError as error:
                delete_warning = error.code
            preview_warning = ""
            preview_key = str(getattr(record, "derived_preview_ref", "") or "").strip()
            if preview_key:
                try:
                    build_attachment_storage(self._ctx).delete_object(key=preview_key)
                except AppError as error:
                    preview_warning = error.code
            metadata_store.mark_deleted(
                task_id=task_id,
                attachment_id=attachment_id,
                deleted_by_user_id=deleted_by,
                warning=delete_warning or preview_warning,
            )
            result = engine.delete_attachment(task_id=task_id, attachment_id=attachment_id)
            try:
                invalidate_default_frontend_cache_store(engine.get_response_cache_store())
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
            engine = build_snapshot_engine(self._ctx)
            storage = build_attachment_storage(self._ctx)
            result = engine.cleanup_stale_attachments(
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


from __future__ import annotations

from datetime import datetime, timezone

from src.app.context import AppContext
from src.commands.model import Command
from src.contexts.attachments.public import (
    get_attachment_snapshot_api,
    get_attachment_storage,
    get_doc_preview_converter,
)
from src.platform.runtime.frontend_cache_invalidation import invalidate_default_frontend_cache_store
from src.services.errors import AppError, TransientError, UserError

get_snapshot_attachment_api = get_attachment_snapshot_api
get_attachment_storage_capability = get_attachment_storage


class GenerateAttachmentPreviewJob:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    @staticmethod
    def _require_text(payload: dict, key: str) -> str:
        value = str(payload.get(key, "")).strip()
        if not value:
            raise UserError(f"{key} is required", code=f"{key}_required")
        return value

    @staticmethod
    def _preview_key(env_name: str, task_id: str, attachment_id: str) -> str:
        return f"attachments/{env_name}/{task_id}/{attachment_id}/preview.pdf"

    def run(self, cmd: Command):
        payload = dict(cmd.payload or {})
        try:
            task_id = self._require_text(payload, "task_id")
            attachment_id = self._require_text(payload, "attachment_id")
            snapshot_attachments = get_snapshot_attachment_api(self._ctx)
            metadata_store = snapshot_attachments.get_attachment_metadata_store()
            lookup = metadata_store.get_by_attachment_id(attachment_id)
            if lookup is None or str(lookup[0]) != task_id:
                raise UserError("Attachment was not found.", code="attachment_not_found")
            _task_id, record = lookup
            kind = str(getattr(record, "kind", "") or "").strip().lower()
            if kind != "doc":
                return {
                    "artifact": "generate_attachment_preview",
                    "status": "ok",
                    "task_id": task_id,
                    "attachment_id": attachment_id,
                    "preview_state": str(getattr(record, "preview_state", "") or "").strip(),
                    "skipped": True,
                    "reason": "attachment_kind_not_doc",
                }
            preview_state = str(getattr(record, "preview_state", "") or "").strip().lower()
            derived_preview_ref = str(getattr(record, "derived_preview_ref", "") or "").strip()
            if preview_state == "ready" and derived_preview_ref:
                return {
                    "artifact": "generate_attachment_preview",
                    "status": "ok",
                    "task_id": task_id,
                    "attachment_id": attachment_id,
                    "preview_state": "ready",
                    "preview_key": derived_preview_ref,
                    "skipped": True,
                    "reason": "preview_already_ready",
                }
            converter = get_doc_preview_converter(self._ctx)
            if converter is None:
                metadata_store.mark_preview_failed(
                    task_id=task_id,
                    attachment_id=attachment_id,
                    error_code="doc_preview_converter_unconfigured",
                    error_message="Doc preview converter is not configured.",
                )
                return {
                    "artifact": "generate_attachment_preview",
                    "status": "failed",
                    "error": {
                        "code": "doc_preview_converter_unconfigured",
                        "message": "Doc preview converter is not configured.",
                    },
                    "failure_kind": "terminal",
                    "retryable": False,
                }
            metadata_store.mark_preview_pending(task_id=task_id, attachment_id=attachment_id)
            storage = get_attachment_storage_capability(self._ctx)
            env_name = str(self._ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev"
            preview_key = self._preview_key(env_name, task_id, attachment_id)
            source_url = storage.generate_read_url(
                key=str(getattr(record, "storage_key", "") or "").strip(),
                filename=str(getattr(record, "filename_display", "") or "").strip(),
                download=False,
            )
            upload_contract = storage.generate_preview_upload_contract(key=preview_key, mime_type="application/pdf")
            target_url = str(upload_contract.get("uploadUrl", "")).strip()
            if not target_url:
                raise TransientError("Preview upload URL is missing.", code="doc_preview_target_url_missing")
            result = converter.convert_doc_to_pdf(
                attachment_id=attachment_id,
                source_url=source_url,
                target_url=target_url,
                source_filename=str(getattr(record, "filename_display", "") or "document.doc"),
                target_filename="preview.pdf",
                request_id=cmd.job_id,
            )
            if str(result.status).strip().lower() != "ready":
                metadata_store.mark_preview_failed(
                    task_id=task_id,
                    attachment_id=attachment_id,
                    error_code=result.error_code or "doc_preview_conversion_failed",
                    error_message=result.error_message or "Converter returned failed status.",
                )
                return {
                    "artifact": "generate_attachment_preview",
                    "status": "failed",
                    "error": {
                        "code": result.error_code or "doc_preview_conversion_failed",
                        "message": result.error_message or "Converter returned failed status.",
                    },
                    "failure_kind": "terminal",
                    "retryable": False,
                }
            metadata_store.mark_preview_ready(
                task_id=task_id,
                attachment_id=attachment_id,
                derived_preview_ref=preview_key,
            )
            snapshot_attachments.attach_file_metadata(
                task_id=task_id,
                attachment=type(record).from_dict(
                    {
                        **record.to_dict(),
                        "preview_state": "ready",
                        "derived_preview_ref": preview_key,
                        "verified_at_utc": getattr(record, "verified_at_utc", None)
                        or datetime.now(timezone.utc),
                    }
                ),
            )
            try:
                invalidate_default_frontend_cache_store(snapshot_attachments.get_response_cache_store())
            except AppError:
                return {
                    "artifact": "generate_attachment_preview",
                    "status": "ok",
                    "task_id": task_id,
                    "attachment_id": attachment_id,
                    "preview_state": "ready",
                    "preview_key": preview_key,
                    "warnings": ["frontend_response_cache_invalidation_failed"],
                }
            return {
                "artifact": "generate_attachment_preview",
                "status": "ok",
                "task_id": task_id,
                "attachment_id": attachment_id,
                "preview_state": "ready",
                "preview_key": preview_key,
            }
        except AppError as error:
            return {
                "artifact": "generate_attachment_preview",
                "status": "failed",
                "error": {"code": error.code, "message": str(error)},
                "failure_kind": "retryable" if isinstance(error, TransientError) else "terminal",
                "retryable": isinstance(error, TransientError),
            }


__all__ = ["GenerateAttachmentPreviewJob"]

from __future__ import annotations

from src.app.context import AppContext
from src.contexts.attachments.public import get_attachment_snapshot_engine, get_attachment_storage
from src.platform.runtime.frontend_cache_invalidation import invalidate_default_frontend_cache_store
from src.services.errors import AppError, UserError

build_snapshot_engine = get_attachment_snapshot_engine
build_attachment_storage = get_attachment_storage


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
            metadata_store.mark_delete_pending(task_id=task_id, attachment_id=attachment_id, deleted_by_user_id=deleted_by)
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

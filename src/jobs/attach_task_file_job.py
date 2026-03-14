from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.app.context import AppContext
from src.entrypoints.http.frontend_response_cache import invalidate_default_frontend_responses
from src.services.errors import AppError, UserError
from src.snapshot_engine import build_snapshot_engine
from src.snapshot_engine.model import AttachmentMeta
from src.services.attachments.policy import build_attachment_capabilities, infer_attachment_kind
from src.services.attachments.contracts import ATTACHMENT_STATUS_READY


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
            )
            engine = build_snapshot_engine(self._ctx)
            metadata_store = engine.get_attachment_metadata_store()
            lookup = metadata_store.get_by_attachment_id(attachment_id)
            if lookup is not None:
                metadata_store.mark_ready(task_id=task_id, attachment_id=attachment_id)
            result = engine.attach_file_metadata(task_id=task_id, attachment=attachment)
            try:
                invalidate_default_frontend_responses(engine)
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

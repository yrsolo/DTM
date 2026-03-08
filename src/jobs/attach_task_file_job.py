from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.app.context import AppContext
from src.services.errors import AppError, UserError
from src.snapshot_engine import build_snapshot_engine
from src.snapshot_engine.model import AttachmentMeta


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
            attachment = AttachmentMeta(
                id=attachment_id,
                key=self._require_text(payload, "key"),
                filename=self._require_text(payload, "filename"),
                mime=self._require_text(payload, "mime"),
                size=self._parse_size(payload),
                uploaded_at_utc=datetime.now(timezone.utc),
                uploaded_by=self._require_text(payload, "uploaded_by"),
                preview=str(payload.get("preview", "")).strip(),
            )
            result = build_snapshot_engine(self._ctx).attach_file_metadata(task_id=task_id, attachment=attachment)
            result["object_key"] = attachment.key
            return result
        except AppError as error:
            return {
                "artifact": "attach_task_file",
                "status": "failed",
                "error": {"code": error.code, "message": str(error)},
            }

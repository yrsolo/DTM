from __future__ import annotations

from src.app.context import AppContext
from src.services.attachments import build_attachment_storage
from src.services.errors import AppError, UserError
from src.snapshot_engine import build_snapshot_engine


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

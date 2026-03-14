from __future__ import annotations

from src.entrypoints.http.access_context import resolve_access_context
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response
from src.services.attachments import AttachmentReadResolver, build_attachment_storage
from src.services.errors import AppError
from src.snapshot_engine import build_snapshot_engine


class TaskAttachmentReadHandler:
    def __init__(self, ctx) -> None:
        self._ctx = ctx

    def _match(self, path: str) -> tuple[str, str] | None:
        normalized = normalize_path(path)
        marker = "/api/task-attachments/"
        if marker not in normalized:
            return None
        suffix = normalized.split(marker, 1)[1]
        parts = [part for part in suffix.split("/") if part]
        if len(parts) != 2:
            return None
        attachment_id, action = parts
        if action not in {"view", "download"}:
            return None
        return attachment_id, action

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        if str(req.method or "").strip().upper() not in {"GET", "ANY"}:
            return None
        matched = self._match(req.path)
        if matched is None:
            return None
        attachment_id, action = matched
        access = resolve_access_context(self._ctx, req)
        try:
            engine = build_snapshot_engine(self._ctx)
            resolver = AttachmentReadResolver(
                metadata_store=engine.get_attachment_metadata_store(),
                storage=build_attachment_storage(self._ctx),
            )
            result = resolver.resolve(attachment_id=attachment_id, access=access, download=(action == "download"))
        except AppError as error:
            status = 403 if error.code == "attachment_access_forbidden" else 404 if error.code == "attachment_not_found" else 503
            return error_response(status, code=error.code, message=str(error))
        return HttpResponse(status=302, body="", headers={"Location": result.url, "Cache-Control": "no-store"})

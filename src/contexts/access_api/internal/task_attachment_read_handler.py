from __future__ import annotations

from src.contexts.attachments.public import (
    get_attachment_read_resolver,
    get_attachment_snapshot_capability,
    get_attachment_storage,
)
from src.entrypoints.http.access_context import resolve_access_context
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response
from src.services.errors import AppError
get_snapshot_capability = get_attachment_snapshot_capability


def get_attachment_storage_capability(ctx):
    return get_attachment_storage(ctx)


def get_attachment_read_capability(ctx):
    return get_attachment_read_resolver(ctx)


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
            resolver = get_attachment_read_capability(self._ctx)
            result = resolver.resolve(attachment_id=attachment_id, access=access, download=(action == "download"))
        except AppError as error:
            if error.code == "attachment_access_forbidden":
                status = 403
            elif error.code == "attachment_not_found":
                status = 404
            elif error.code == "attachment_preview_pending":
                status = 409
            else:
                status = 503
            return error_response(status, code=error.code, message=str(error))
        return HttpResponse(status=302, body="", headers={"Location": result.url, "Cache-Control": "no-store"})

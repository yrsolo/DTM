"""Composite browser-route handler owned by the access_api context."""

from __future__ import annotations

from src.entrypoints.http.dto import HttpRequest, HttpResponse

from .frontend_root_handler import FrontendRootHandler
from .frontend_v2_handler import FrontendV2Handler
from .info_handler import InfoHandler
from .people_snapshot_handler import PeopleSnapshotHandler
from .task_attachment_read_handler import TaskAttachmentReadHandler


class BrowserRoutesHandler:
    """Dispatch browser-facing read routes inside the owning access_api module."""

    def __init__(self, ctx) -> None:
        self._handlers = [
            FrontendRootHandler(ctx).handle,
            FrontendV2Handler(ctx).handle,
            InfoHandler(ctx).handle,
            PeopleSnapshotHandler(ctx).handle,
            TaskAttachmentReadHandler(ctx).handle,
        ]

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        for handler in self._handlers:
            response = handler(req)
            if response is not None:
                return response
        return None


__all__ = ["BrowserRoutesHandler"]

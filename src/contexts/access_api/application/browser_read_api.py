"""Application-owned browser read entry for the access API context."""

from __future__ import annotations

from src.entrypoints.http.dto import HttpRequest, HttpResponse

from ..internal.browser_root_read_api import BrowserRootReadApi
from ..internal.operational_info_read_api import OperationalInfoReadApi
from ..internal.people_directory_read_api import PeopleDirectoryReadApi
from ..internal.primary_task_list_read_api import PrimaryTaskListReadApi
from ..internal.task_attachment_read_api import TaskAttachmentReadApi


class BrowserReadApi:
    """Dispatch browser-facing reads through the access_api application layer."""

    def __init__(self, ctx) -> None:
        self._read_routes = [
            BrowserRootReadApi(ctx).handle,
            PrimaryTaskListReadApi(ctx).handle,
            OperationalInfoReadApi(ctx).handle,
            PeopleDirectoryReadApi(ctx).handle,
            TaskAttachmentReadApi(ctx).handle,
        ]

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        for route in self._read_routes:
            response = route(req)
            if response is not None:
                return response
        return None


__all__ = ["BrowserReadApi"]

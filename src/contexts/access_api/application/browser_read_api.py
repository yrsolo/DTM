"""Application-owned primary browser read surface for the access API context."""

from __future__ import annotations

from src.entrypoints.http.dto import HttpRequest, HttpResponse

from ..internal.browser_root_read_api import BrowserRootReadApi
from ..internal.operational_info_read_api import OperationalInfoReadApi
from ..internal.people_directory_read_api import PeopleDirectoryReadApi
from ..internal.primary_task_list_read_api import PrimaryTaskListReadApi
from ..internal.task_attachment_read_api import TaskAttachmentReadApi


class PrimaryBrowserReadApi:
    """Own browser-facing reads through the access_api application layer."""

    def __init__(self, ctx) -> None:
        self._root_read = BrowserRootReadApi(ctx)
        self._primary_task_list_read = PrimaryTaskListReadApi(ctx)
        self._operational_info_read = OperationalInfoReadApi(ctx)
        self._people_directory_read = PeopleDirectoryReadApi(ctx)
        self._task_attachment_read = TaskAttachmentReadApi(ctx)

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        for route in (
            self._root_read.handle,
            self._primary_task_list_read.handle,
            self._operational_info_read.handle,
            self._people_directory_read.handle,
            self._task_attachment_read.handle,
        ):
            response = route(req)
            if response is not None:
                return response
        return None


__all__ = ["PrimaryBrowserReadApi"]

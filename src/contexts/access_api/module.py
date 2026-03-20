"""Module surface for the access API context."""

from __future__ import annotations

from dataclasses import dataclass

from .internal.browser_routes import BrowserRoutesHandler
from .internal.frontend_root_handler import FrontendRootHandler
from .internal.frontend_v2_handler import FrontendV2Handler
from .internal.info_handler import InfoHandler
from .internal.people_snapshot_handler import PeopleSnapshotHandler
from .internal.task_attachment_read_handler import TaskAttachmentReadHandler


@dataclass(frozen=True, slots=True)
class AccessApiModule:
    """Own the browser-facing access API surface for the active runtime."""

    name: str = "access_api"

    def build_browser_routes_handler(self, ctx):
        return BrowserRoutesHandler(ctx)

    def build_frontend_root_handler(self, ctx):
        return FrontendRootHandler(ctx)

    def build_frontend_v2_handler(self, ctx):
        return FrontendV2Handler(ctx)

    def build_info_handler(self, ctx):
        return InfoHandler(ctx)

    def build_people_snapshot_handler(self, ctx):
        return PeopleSnapshotHandler(ctx)

    def build_task_attachment_read_handler(self, ctx):
        return TaskAttachmentReadHandler(ctx)


def get_module() -> AccessApiModule:
    """Return the canonical module surface for the access API context."""

    return AccessApiModule()

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

    def browser_routes(self, ctx):
        return BrowserRoutesHandler(ctx)

    def frontend_root_handler(self, ctx):
        return FrontendRootHandler(ctx)

    def frontend_v2_handler(self, ctx):
        return FrontendV2Handler(ctx)

    def info_handler(self, ctx):
        return InfoHandler(ctx)

    def people_snapshot_handler(self, ctx):
        return PeopleSnapshotHandler(ctx)

    def task_attachment_read_handler(self, ctx):
        return TaskAttachmentReadHandler(ctx)


def get_module() -> AccessApiModule:
    """Return the canonical module surface for the access API context."""

    return AccessApiModule()

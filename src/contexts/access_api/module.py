"""Local builder for the access API context."""

from __future__ import annotations

from dataclasses import dataclass

from src.entrypoints.http.frontend_compat_handlers import FrontendRootHandler
from src.entrypoints.http.frontend_v2_handler import FrontendV2Handler
from src.entrypoints.http.info_handler import InfoHandler
from src.entrypoints.http.people_snapshot_handler import PeopleSnapshotHandler
from src.entrypoints.http.task_attachment_read_handler import TaskAttachmentReadHandler


@dataclass(frozen=True, slots=True)
class AccessApiModule:
    """Context-local builder bundle used during staged migration."""

    name: str = "access_api"

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
    """Return the local module instance for the access API context."""

    return AccessApiModule()

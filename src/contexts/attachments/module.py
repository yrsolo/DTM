"""Local builder for the transitional attachments context."""

from __future__ import annotations

from dataclasses import dataclass

from src.app.context import AppContext
from src.services.attachments import (
    AttachmentFinalizeService,
    AttachmentReadResolver,
    build_attachment_storage,
)
from src.snapshot_engine import build_snapshot_engine


@dataclass(slots=True)
class AttachmentsModule:
    """Context-local builder used during staged migration."""

    ctx: AppContext
    name: str = "attachments"

    def snapshot_engine(self):
        return build_snapshot_engine(self.ctx)

    def metadata_store(self):
        return self.snapshot_engine().get_attachment_metadata_store()

    def storage(self):
        return build_attachment_storage(self.ctx)

    def finalize_service(self) -> AttachmentFinalizeService:
        return AttachmentFinalizeService(
            storage=self.storage(),
            metadata_store=self.metadata_store(),
        )

    def read_resolver(self) -> AttachmentReadResolver:
        return AttachmentReadResolver(
            metadata_store=self.metadata_store(),
            storage=self.storage(),
        )


def get_module(ctx: AppContext) -> AttachmentsModule:
    """Return the local attachments module builder."""

    return AttachmentsModule(ctx=ctx)

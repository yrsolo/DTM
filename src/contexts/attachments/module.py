"""Module surface for the attachments context."""

from __future__ import annotations

from dataclasses import dataclass

from src.app.context import AppContext
from src.contexts.snapshot.module import get_attachment_api
from src.infra.doc_preview_converter import DocPreviewConverter

from .internal import AttachmentFinalizeService, AttachmentReadResolver, build_attachment_storage


@dataclass(slots=True)
class AttachmentsModule:
    """Own attachment publication, storage, and read resolution assembly."""

    ctx: AppContext
    name: str = "attachments"

    def snapshot_api(self):
        return get_attachment_api(self.ctx)

    def command_flow(self):
        from .application.command_flow import AttachmentCommandFlow

        return AttachmentCommandFlow(self.ctx)

    def metadata_store(self):
        return self.snapshot_api().get_attachment_metadata_store()

    def storage(self):
        return build_attachment_storage(self.ctx)

    def doc_preview_converter(self):
        explicit = self.ctx.deps.get("doc_preview_converter")
        if explicit is not None:
            return explicit
        cached = self.ctx.deps.get("attachments_doc_preview_converter")
        if cached is not None:
            return cached
        base_url = str(self.ctx.deps.get("doc_preview_converter_url", "") or "").strip()
        if not base_url:
            return None
        converter = DocPreviewConverter(
            base_url=base_url,
            shared_token=str(self.ctx.deps.get("doc_preview_converter_shared_token", "") or "").strip(),
        )
        self.ctx.deps["attachments_doc_preview_converter"] = converter
        return converter

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
    """Return the canonical module surface for the attachments context."""

    return AttachmentsModule(ctx=ctx)

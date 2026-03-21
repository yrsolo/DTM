"""Application-owned command flow for the attachments context."""

from __future__ import annotations

from src.app.context import AppContext
from src.commands.types import (
    ATTACH_TASK_FILE,
    CLEANUP_TASK_ATTACHMENTS,
    DELETE_TASK_ATTACHMENT,
    GENERATE_ATTACHMENT_PREVIEW,
)

from ..internal.job_runners import (
    AttachTaskFileJob,
    CleanupTaskAttachmentsJob,
    DeleteTaskAttachmentJob,
)
from ..internal.preview_job import GenerateAttachmentPreviewJob


class AttachmentCommandFlow:
    """Expose attachment mutations through one module-owned command flow."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def attach_file(self) -> AttachTaskFileJob:
        return AttachTaskFileJob(self._ctx)

    def delete_attachment(self) -> DeleteTaskAttachmentJob:
        return DeleteTaskAttachmentJob(self._ctx)

    def cleanup_stale_attachments(self) -> CleanupTaskAttachmentsJob:
        return CleanupTaskAttachmentsJob(self._ctx)

    def generate_preview(self) -> GenerateAttachmentPreviewJob:
        return GenerateAttachmentPreviewJob(self._ctx)

    def command_handlers(self) -> dict[str, object]:
        return {
            ATTACH_TASK_FILE: self.attach_file(),
            DELETE_TASK_ATTACHMENT: self.delete_attachment(),
            CLEANUP_TASK_ATTACHMENTS: self.cleanup_stale_attachments(),
            GENERATE_ATTACHMENT_PREVIEW: self.generate_preview(),
        }


__all__ = ["AttachmentCommandFlow"]

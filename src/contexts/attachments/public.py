"""Public facade for the attachments context."""

from __future__ import annotations

from src.app.context import AppContext

from .internal.contracts import SUPPORTED_ATTACHMENT_MIME_TYPES

from .module import get_module


def get_public_api(ctx: AppContext):
    """Return the local module builder without leaking internals."""

    return get_module(ctx)


def get_attachment_storage(ctx: AppContext):
    """Return the context-owned storage adapter."""

    return get_public_api(ctx).storage()


def get_attachment_metadata_store(ctx: AppContext):
    """Return the context-owned metadata store."""

    return get_public_api(ctx).metadata_store()


def get_attachment_finalize_service(ctx: AppContext):
    """Return the context-owned finalize service."""

    return get_public_api(ctx).finalize_service()


def get_attachment_read_resolver(ctx: AppContext):
    """Return the context-owned read resolver."""

    return get_public_api(ctx).read_resolver()


def get_supported_attachment_mime_types() -> frozenset[str]:
    """Return the public mime-type contract owned by the attachments context."""

    return SUPPORTED_ATTACHMENT_MIME_TYPES


def get_attachment_snapshot_capability(ctx: AppContext):
    """Return the attachment-scoped snapshot capability."""

    return get_public_api(ctx).snapshot_capability()


def get_attach_task_file_job(ctx: AppContext):
    """Return the owning attachment job runner for attach-file mutations."""

    from src.jobs.attach_task_file_job import AttachTaskFileJob

    return AttachTaskFileJob(ctx)


def get_delete_task_attachment_job(ctx: AppContext):
    """Return the owning attachment job runner for delete mutations."""

    from src.jobs.delete_task_attachment_job import DeleteTaskAttachmentJob

    return DeleteTaskAttachmentJob(ctx)


def get_cleanup_task_attachments_job(ctx: AppContext):
    """Return the owning attachment job runner for cleanup mutations."""

    from src.jobs.cleanup_task_attachments_job import CleanupTaskAttachmentsJob

    return CleanupTaskAttachmentsJob(ctx)


def get_generate_attachment_preview_job(ctx: AppContext):
    """Return the owning attachment job runner for preview generation."""

    from src.jobs.generate_attachment_preview_job import GenerateAttachmentPreviewJob

    return GenerateAttachmentPreviewJob(ctx)

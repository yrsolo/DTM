"""Public facade for the attachments context."""

from __future__ import annotations

from src.platform.context import AppContext

from .internal.contracts import SUPPORTED_ATTACHMENT_MIME_TYPES

from .module import get_module


def get_public_api(ctx: AppContext):
    """Return the local module surface without leaking internals."""

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


def get_doc_preview_converter(ctx: AppContext):
    """Return the context-owned doc preview converter when configured."""

    return get_public_api(ctx).doc_preview_converter()


def get_supported_attachment_mime_types() -> frozenset[str]:
    """Return the public mime-type contract owned by the attachments context."""

    return SUPPORTED_ATTACHMENT_MIME_TYPES


def get_attachment_snapshot_api(ctx: AppContext):
    """Return the attachment-scoped snapshot API."""

    return get_public_api(ctx).snapshot_api()


def get_attachment_command_flow(ctx: AppContext):
    """Return the module-owned attachment command flow."""

    return get_public_api(ctx).command_flow()


def get_command_handlers(ctx: AppContext) -> dict[str, object]:
    """Return the attachment-owned queue command handlers."""

    return get_attachment_command_flow(ctx).command_handlers()

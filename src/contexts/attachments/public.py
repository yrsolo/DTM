"""Public facade for the attachments context."""

from __future__ import annotations

from src.platform.context import AppContext

from .internal.contracts import SUPPORTED_ATTACHMENT_MIME_TYPES
from .module import get_module

def get_attachment_api(ctx: AppContext):
    """Return the canonical attachments surface."""

    return get_module(ctx)

def get_supported_attachment_mime_types() -> frozenset[str]:
    """Return the public mime-type contract owned by the attachments context."""

    return SUPPORTED_ATTACHMENT_MIME_TYPES


def get_command_handlers(ctx: AppContext) -> dict[str, object]:
    """Return the attachment-owned queue command handlers."""

    return get_attachment_api(ctx).command_flow().command_handlers()


__all__ = [
    "get_attachment_api",
    "get_command_handlers",
    "get_supported_attachment_mime_types",
]

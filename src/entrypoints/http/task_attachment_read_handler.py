"""Compatibility wrapper for the access-api-owned attachment read handler."""

from src.contexts.access_api.internal.task_attachment_read_handler import (
    TaskAttachmentReadHandler,
    build_attachment_read_resolver,
    build_attachment_storage,
    build_snapshot_engine,
)

__all__ = [
    "TaskAttachmentReadHandler",
    "build_attachment_read_resolver",
    "build_attachment_storage",
    "build_snapshot_engine",
]

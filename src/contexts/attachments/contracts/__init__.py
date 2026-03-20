"""Contracts and public policy helpers for the attachments context."""

from src.contexts.attachments.internal import (
    ATTACHMENT_STATUS_DELETED,
    ATTACHMENT_STATUS_DELETE_PENDING,
    ATTACHMENT_STATUS_FAILED,
    ATTACHMENT_STATUS_PENDING_UPLOAD,
    ATTACHMENT_STATUS_READY,
    ATTACHMENT_STATUS_UPLOADED_UNVERIFIED,
    AttachmentMetadataStore,
    attachment_projection_visible,
    build_attachment_capabilities,
    canonicalize_attachment_mime,
    infer_attachment_kind,
)

__all__ = [
    "ATTACHMENT_STATUS_DELETED",
    "ATTACHMENT_STATUS_DELETE_PENDING",
    "ATTACHMENT_STATUS_FAILED",
    "ATTACHMENT_STATUS_PENDING_UPLOAD",
    "ATTACHMENT_STATUS_READY",
    "ATTACHMENT_STATUS_UPLOADED_UNVERIFIED",
    "AttachmentMetadataStore",
    "attachment_projection_visible",
    "build_attachment_capabilities",
    "canonicalize_attachment_mime",
    "infer_attachment_kind",
]

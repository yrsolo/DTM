from __future__ import annotations

from src.entrypoints.http.access_context import AccessContext
from src.platform.errors import UserError

from .contracts import (
    ATTACHMENT_KIND_DOC,
    ATTACHMENT_KIND_DOCX,
    ATTACHMENT_KIND_IMAGE,
    ATTACHMENT_KIND_PDF,
    ATTACHMENT_MIME_DOC,
    ATTACHMENT_MIME_DOCX,
    ATTACHMENT_MIME_JPEG,
    ATTACHMENT_MIME_PDF,
    ATTACHMENT_MIME_PNG,
    ATTACHMENT_MIME_WEBP,
    ATTACHMENT_STATUS_READY,
    SUPPORTED_ATTACHMENT_MIME_TYPES,
)


def canonicalize_attachment_mime(value: str) -> str:
    mime = str(value or "").strip().lower()
    if mime not in SUPPORTED_ATTACHMENT_MIME_TYPES:
        raise UserError("Unsupported attachment mime type.", code="attachment_mime_unsupported")
    return mime


def infer_attachment_kind(mime_type: str) -> str:
    canonical = canonicalize_attachment_mime(mime_type)
    if canonical == ATTACHMENT_MIME_DOCX:
        return ATTACHMENT_KIND_DOCX
    if canonical == ATTACHMENT_MIME_DOC:
        return ATTACHMENT_KIND_DOC
    if canonical == ATTACHMENT_MIME_PDF:
        return ATTACHMENT_KIND_PDF
    if canonical in {ATTACHMENT_MIME_PNG, ATTACHMENT_MIME_JPEG, ATTACHMENT_MIME_WEBP}:
        return ATTACHMENT_KIND_IMAGE
    raise UserError("Unsupported attachment kind.", code="attachment_kind_unsupported")


def build_attachment_capabilities(kind: str) -> list[str]:
    if str(kind or "").strip() == ATTACHMENT_KIND_DOCX:
        return ["browser_view", "download", "docx_view"]
    if str(kind or "").strip() == ATTACHMENT_KIND_DOC:
        return ["browser_view", "download", "pdf_preview"]
    if str(kind or "").strip() == ATTACHMENT_KIND_PDF:
        return ["browser_view", "download", "pdf_view"]
    if str(kind or "").strip() == ATTACHMENT_KIND_IMAGE:
        return ["browser_view", "download", "image_inline"]
    return ["download"]


def attachment_projection_visible(record) -> bool:  # noqa: ANN001
    return bool(getattr(record, "snapshot_visible", False)) and str(getattr(record, "status", "")).strip() == ATTACHMENT_STATUS_READY


def attachment_read_allowed(access: AccessContext, record) -> bool:  # noqa: ANN001
    if not attachment_projection_visible(record):
        return False
    return bool(access.trusted_ingress) and bool(access.authenticated) and str(access.mode) == "full" and str(access.user_status or "") == "approved"

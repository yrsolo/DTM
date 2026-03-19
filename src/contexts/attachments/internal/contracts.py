from __future__ import annotations

ATTACHMENT_STATUS_PENDING_UPLOAD = "pending_upload"
ATTACHMENT_STATUS_UPLOADED_UNVERIFIED = "uploaded_unverified"
ATTACHMENT_STATUS_READY = "ready"
ATTACHMENT_STATUS_DELETE_PENDING = "delete_pending"
ATTACHMENT_STATUS_DELETED = "deleted"
ATTACHMENT_STATUS_FAILED = "failed"

ATTACHMENT_KIND_DOCX = "docx"
ATTACHMENT_KIND_DOC = "doc"
ATTACHMENT_KIND_PDF = "pdf"
ATTACHMENT_KIND_IMAGE = "image"

ATTACHMENT_MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
ATTACHMENT_MIME_DOC = "application/msword"
ATTACHMENT_MIME_PDF = "application/pdf"
ATTACHMENT_MIME_PNG = "image/png"
ATTACHMENT_MIME_JPEG = "image/jpeg"
ATTACHMENT_MIME_WEBP = "image/webp"

SUPPORTED_ATTACHMENT_MIME_TYPES = frozenset(
    {
        ATTACHMENT_MIME_DOCX,
        ATTACHMENT_MIME_DOC,
        ATTACHMENT_MIME_PDF,
        ATTACHMENT_MIME_PNG,
        ATTACHMENT_MIME_JPEG,
        ATTACHMENT_MIME_WEBP,
    }
)

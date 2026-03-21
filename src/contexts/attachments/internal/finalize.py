from __future__ import annotations

from dataclasses import dataclass

from src.platform.errors import UserError

from .policy import canonicalize_attachment_mime


@dataclass(frozen=True, slots=True)
class VerifiedAttachmentObject:
    content_length: int
    mime_type: str
    storage_etag: str
    storage_version: str


class AttachmentFinalizeService:
    def __init__(self, *, storage, metadata_store) -> None:  # noqa: ANN001
        self._storage = storage
        self._metadata_store = metadata_store

    def finalize(self, *, task_id: str, attachment_id: str) -> VerifiedAttachmentObject:
        lookup = self._metadata_store.get_by_attachment_id(attachment_id)
        if lookup is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        record_task_id, record = lookup
        if str(record_task_id) != str(task_id or "").strip():
            raise UserError("Attachment does not belong to the specified task.", code="attachment_task_mismatch")
        head = self._storage.head_object(key=record.storage_key)
        actual_size = max(int(head.get("ContentLength", 0) or 0), 0)
        if actual_size != int(record.size_bytes):
            self._metadata_store.mark_failed(task_id=record.task_id, attachment_id=record.attachment_id, error_code="attachment_size_mismatch", error_message="Uploaded object size does not match requested size.")
            raise UserError("Uploaded object size does not match requested size.", code="attachment_size_mismatch")
        actual_mime = canonicalize_attachment_mime(str(head.get("ContentType", "")).strip() or record.mime_type)
        if actual_mime != canonicalize_attachment_mime(record.mime_type):
            self._metadata_store.mark_failed(task_id=record.task_id, attachment_id=record.attachment_id, error_code="attachment_mime_mismatch", error_message="Uploaded object mime type does not match requested mime type.")
            raise UserError("Uploaded object mime type does not match requested mime type.", code="attachment_mime_mismatch")
        storage_etag = str(head.get("ETag", "")).strip().strip('"')
        storage_version = str(head.get("VersionId", "")).strip()
        self._metadata_store.mark_uploaded_unverified(task_id=record.task_id, attachment_id=record.attachment_id, storage_etag=storage_etag, storage_version=storage_version)
        return VerifiedAttachmentObject(content_length=actual_size, mime_type=actual_mime, storage_etag=storage_etag, storage_version=storage_version)

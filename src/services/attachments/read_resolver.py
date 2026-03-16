from __future__ import annotations

from dataclasses import dataclass

from src.services.attachments.contracts import ATTACHMENT_KIND_DOC
from src.services.attachments.policy import attachment_read_allowed
from src.services.errors import UserError


@dataclass(frozen=True, slots=True)
class AttachmentReadResult:
    url: str
    filename: str
    download: bool


class AttachmentReadResolver:
    def __init__(self, *, metadata_store, storage) -> None:  # noqa: ANN001
        self._metadata_store = metadata_store
        self._storage = storage

    def resolve(self, *, attachment_id: str, access, download: bool) -> AttachmentReadResult:  # noqa: ANN001
        lookup = self._metadata_store.get_by_attachment_id(attachment_id)
        if lookup is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        _task_id, record = lookup
        if not attachment_read_allowed(access, record):
            raise UserError("Attachment access is forbidden.", code="attachment_access_forbidden")
        kind = str(getattr(record, "kind", "") or "").strip()
        if kind == ATTACHMENT_KIND_DOC and not download:
            preview_state = str(getattr(record, "preview_state", "") or "").strip().lower()
            derived_preview_ref = str(getattr(record, "derived_preview_ref", "") or "").strip()
            if preview_state == "ready" and derived_preview_ref:
                return AttachmentReadResult(
                    url=self._storage.generate_read_url(
                        key=derived_preview_ref,
                        filename="preview.pdf",
                        download=False,
                    ),
                    filename="preview.pdf",
                    download=False,
                )
            if preview_state == "pending":
                raise UserError("Attachment preview is still being generated.", code="attachment_preview_pending")
            raise UserError("Attachment preview is unavailable.", code="attachment_preview_unavailable")
        return AttachmentReadResult(
            url=self._storage.generate_read_url(
                key=record.storage_key,
                filename=record.filename_display,
                download=bool(download),
            ),
            filename=record.filename_display,
            download=bool(download),
        )

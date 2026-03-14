from __future__ import annotations

from dataclasses import dataclass

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
        return AttachmentReadResult(
            url=self._storage.generate_read_url(
                key=record.storage_key,
                filename=record.filename_display,
                download=bool(download),
            ),
            filename=record.filename_display,
            download=bool(download),
        )

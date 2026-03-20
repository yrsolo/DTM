from __future__ import annotations

from datetime import datetime, timezone

from src.contexts.snapshot.contracts import AttachmentMeta, ExtraSnapshot, TaskExtra
from src.services.errors import UserError

from .contracts import (
    ATTACHMENT_STATUS_DELETED,
    ATTACHMENT_STATUS_DELETE_PENDING,
    ATTACHMENT_STATUS_FAILED,
    ATTACHMENT_STATUS_PENDING_UPLOAD,
    ATTACHMENT_STATUS_READY,
    ATTACHMENT_STATUS_UPLOADED_UNVERIFIED,
)
from .policy import build_attachment_capabilities, infer_attachment_kind


class AttachmentMetadataStore:
    def __init__(self, extra_store, *, bucket: str) -> None:  # noqa: ANN001
        self._extra_store = extra_store
        self._bucket = str(bucket or "").strip()

    def _snapshot(self) -> ExtraSnapshot:
        return self._extra_store.get_snapshot()

    def _put(self, snapshot: ExtraSnapshot) -> None:
        self._extra_store.put_snapshot(snapshot)

    @staticmethod
    def _replace_task_item(snapshot: ExtraSnapshot, *, task_id: str, attachments: list[AttachmentMeta], now: datetime) -> ExtraSnapshot:
        items = dict(snapshot.items_by_task_id or {})
        current = items.get(task_id) or TaskExtra(task_id=task_id)
        items[task_id] = TaskExtra(task_id=task_id, orphaned=bool(current.orphaned), updated_at_utc=now, attachments=list(attachments), docs=list(current.docs), links=list(current.links), notes=str(current.notes), artifacts=list(current.artifacts))
        return ExtraSnapshot(version=max(int(snapshot.version or 2), 1), updated_at_utc=now, items_by_task_id=items)

    @staticmethod
    def _sort(items: list[AttachmentMeta]) -> list[AttachmentMeta]:
        return sorted(list(items or []), key=lambda item: (str(getattr(item, "sort_key", "") or ""), getattr(item, "uploaded_at_utc", datetime.now(timezone.utc)).isoformat(), str(getattr(item, "attachment_id", getattr(item, "id", "")) or "")))

    def get_by_attachment_id(self, attachment_id: str) -> tuple[str, AttachmentMeta] | None:
        lookup = str(attachment_id or "").strip()
        if not lookup:
            return None
        snapshot = self._snapshot()
        for task_id, extra in dict(snapshot.items_by_task_id or {}).items():
            for item in list(extra.attachments or []):
                if str(getattr(item, "attachment_id", getattr(item, "id", "")) or "") == lookup:
                    return str(task_id), item
        return None

    def list_by_task_id(self, task_id: str) -> list[AttachmentMeta]:
        snapshot = self._snapshot()
        extra = dict(snapshot.items_by_task_id or {}).get(str(task_id or "").strip())
        if extra is None:
            return []
        return self._sort(list(extra.attachments or []))

    def create_pending(self, *, task_id: str, attachment_id: str, filename: str, mime_type: str, size_bytes: int, storage_key: str, uploaded_by_user_id: str) -> AttachmentMeta:
        task_key = str(task_id or "").strip()
        if not task_key:
            raise UserError("task_id is required", code="task_id_required")
        now = datetime.now(timezone.utc)
        existing = self.list_by_task_id(task_key)
        kind = infer_attachment_kind(mime_type)
        record = AttachmentMeta(id=str(attachment_id or "").strip(), task_id=task_key, key=str(storage_key or "").strip(), storage_key=str(storage_key or "").strip(), storage_bucket=self._bucket, filename=str(filename or "").strip(), filename_original=str(filename or "").strip(), filename_display=str(filename or "").strip(), mime=str(mime_type or "").strip(), mime_type=str(mime_type or "").strip(), kind=kind, size=max(int(size_bytes or 0), 0), size_bytes=max(int(size_bytes or 0), 0), uploaded_at_utc=now, uploaded_by=str(uploaded_by_user_id or "").strip(), uploaded_by_user_id=str(uploaded_by_user_id or "").strip(), status=ATTACHMENT_STATUS_PENDING_UPLOAD, snapshot_visible=False, preview_capabilities=build_attachment_capabilities(kind), sort_key=now.isoformat(), summary_status="none", extracted_text_status="none", preview_state="none")
        updated = [item for item in existing if str(item.attachment_id) != record.attachment_id]
        updated.append(record)
        snapshot = self._snapshot()
        self._put(self._replace_task_item(snapshot, task_id=task_key, attachments=self._sort(updated), now=now))
        return record

    def mark_uploaded_unverified(self, *, task_id: str, attachment_id: str, storage_etag: str, storage_version: str) -> AttachmentMeta:
        return self._update_status(task_id=task_id, attachment_id=attachment_id, status=ATTACHMENT_STATUS_UPLOADED_UNVERIFIED, snapshot_visible=False, storage_etag=storage_etag, storage_version=storage_version, verified_at_utc=datetime.now(timezone.utc), error_code="", error_message="")

    def mark_failed(self, *, task_id: str, attachment_id: str, error_code: str, error_message: str) -> AttachmentMeta:
        return self._update_status(task_id=task_id, attachment_id=attachment_id, status=ATTACHMENT_STATUS_FAILED, snapshot_visible=False, error_code=error_code, error_message=error_message)

    def mark_ready(self, *, task_id: str, attachment_id: str) -> AttachmentMeta:
        return self._update_status(task_id=task_id, attachment_id=attachment_id, status=ATTACHMENT_STATUS_READY, snapshot_visible=True, verified_at_utc=datetime.now(timezone.utc), error_code="", error_message="")

    def mark_delete_pending(self, *, task_id: str, attachment_id: str, deleted_by_user_id: str) -> AttachmentMeta:
        return self._update_status(task_id=task_id, attachment_id=attachment_id, status=ATTACHMENT_STATUS_DELETE_PENDING, snapshot_visible=False, deleted_by_user_id=str(deleted_by_user_id or "").strip(), deleted_at_utc=datetime.now(timezone.utc))

    def mark_deleted(self, *, task_id: str, attachment_id: str, deleted_by_user_id: str, warning: str = "") -> AttachmentMeta:
        warnings = [warning] if str(warning or "").strip() else []
        return self._update_status(task_id=task_id, attachment_id=attachment_id, status=ATTACHMENT_STATUS_DELETED, snapshot_visible=False, deleted_by_user_id=str(deleted_by_user_id or "").strip(), deleted_at_utc=datetime.now(timezone.utc), warnings=warnings)

    def mark_preview_pending(self, *, task_id: str, attachment_id: str) -> AttachmentMeta:
        return self._update_fields(task_id=task_id, attachment_id=attachment_id, preview_state="pending")

    def mark_preview_ready(self, *, task_id: str, attachment_id: str, derived_preview_ref: str) -> AttachmentMeta:
        return self._update_fields(task_id=task_id, attachment_id=attachment_id, preview_state="ready", derived_preview_ref=str(derived_preview_ref or "").strip(), error_code="", error_message="")

    def mark_preview_failed(self, *, task_id: str, attachment_id: str, error_code: str, error_message: str) -> AttachmentMeta:
        return self._update_fields(task_id=task_id, attachment_id=attachment_id, preview_state="failed", error_code=str(error_code or "").strip(), error_message=str(error_message or "").strip())

    def _update_status(self, *, task_id: str, attachment_id: str, status: str, snapshot_visible: bool, **changes) -> AttachmentMeta:
        task_key = str(task_id or "").strip()
        lookup = str(attachment_id or "").strip()
        if not task_key or not lookup:
            raise UserError("attachment_id and task_id are required", code="attachment_lookup_required")
        snapshot = self._snapshot()
        existing = dict(snapshot.items_by_task_id or {}).get(task_key)
        if existing is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        now = datetime.now(timezone.utc)
        updated_list: list[AttachmentMeta] = []
        updated_item: AttachmentMeta | None = None
        for item in list(existing.attachments or []):
            if str(item.attachment_id) != lookup:
                updated_list.append(item)
                continue
            payload = dict(item.to_dict())
            payload.update(changes)
            payload["status"] = status
            payload["snapshot_visible"] = bool(snapshot_visible)
            payload["task_id"] = task_key
            updated_item = AttachmentMeta.from_dict(payload)
            updated_list.append(updated_item)
        if updated_item is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        self._put(self._replace_task_item(snapshot, task_id=task_key, attachments=self._sort(updated_list), now=now))
        return updated_item

    def _update_fields(self, *, task_id: str, attachment_id: str, **changes) -> AttachmentMeta:
        task_key = str(task_id or "").strip()
        lookup = str(attachment_id or "").strip()
        if not task_key or not lookup:
            raise UserError("attachment_id and task_id are required", code="attachment_lookup_required")
        snapshot = self._snapshot()
        existing = dict(snapshot.items_by_task_id or {}).get(task_key)
        if existing is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        now = datetime.now(timezone.utc)
        updated_list: list[AttachmentMeta] = []
        updated_item: AttachmentMeta | None = None
        for item in list(existing.attachments or []):
            if str(item.attachment_id) != lookup:
                updated_list.append(item)
                continue
            payload = dict(item.to_dict())
            payload.update(changes)
            payload["task_id"] = task_key
            updated_item = AttachmentMeta.from_dict(payload)
            updated_list.append(updated_item)
        if updated_item is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        self._put(self._replace_task_item(snapshot, task_id=task_key, attachments=self._sort(updated_list), now=now))
        return updated_item

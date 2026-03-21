"""Attachment mutation service for snapshot-owned projection updates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.contexts.attachments.contracts import (
    ATTACHMENT_STATUS_DELETED,
    ATTACHMENT_STATUS_PENDING_UPLOAD,
    ATTACHMENT_STATUS_READY,
    ATTACHMENT_STATUS_UPLOADED_UNVERIFIED,
    AttachmentMetadataStore,
)
from src.contexts.snapshot.internal.engine.model import AttachmentMeta, ExtraSnapshot, TaskExtra
from src.platform.errors import AppError, UserError


@dataclass(slots=True)
class SnapshotAttachmentMutationService:
    """Own attachment mutation semantics for the snapshot projection."""

    attachment_bucket: str
    raw_cache: Any
    prep_cache: Any
    extra_store: Any
    prep_builder: Any

    def get_attachment_metadata_store(self) -> AttachmentMetadataStore:
        return AttachmentMetadataStore(self.extra_store, bucket=self.attachment_bucket)

    def attach_file_metadata(self, *, task_id: str, attachment: AttachmentMeta) -> dict[str, Any]:
        raw = self.raw_cache.get()
        if raw is None:
            raise UserError("Raw snapshot is unavailable.", code="raw_snapshot_unavailable")
        task_key = str(task_id or "").strip()
        if not task_key or task_key not in raw.tasks_by_id:
            raise UserError("Task was not found in current snapshot.", code="task_not_found")
        metadata_store = self.get_attachment_metadata_store()
        existing = metadata_store.list_by_task_id(task_key)
        payload = attachment.to_dict()
        payload["task_id"] = task_key
        payload["status"] = ATTACHMENT_STATUS_READY
        payload["snapshot_visible"] = True
        ready_attachment = AttachmentMeta.from_dict(payload)
        extra_snapshot = self.extra_store.get_snapshot()
        items_by_task_id = dict(extra_snapshot.items_by_task_id)
        current = items_by_task_id.get(task_key) or TaskExtra(task_id=task_key)
        attachments = [
            item
            for item in list(existing or [])
            if str(item.attachment_id) != str(ready_attachment.attachment_id)
        ]
        attachments.append(ready_attachment)
        attachments.sort(
            key=lambda item: (
                str(item.sort_key),
                item.uploaded_at_utc.isoformat(),
                item.attachment_id,
            )
        )
        items_by_task_id[task_key] = TaskExtra(
            task_id=current.task_id,
            orphaned=bool(current.orphaned),
            updated_at_utc=datetime.now(timezone.utc),
            attachments=attachments,
            docs=list(current.docs),
            links=list(current.links),
            notes=str(current.notes),
            artifacts=list(current.artifacts),
        )
        self.extra_store.put_snapshot(
            ExtraSnapshot(
                version=max(int(extra_snapshot.version or 2), 1),
                updated_at_utc=datetime.now(timezone.utc),
                items_by_task_id=items_by_task_id,
            )
        )
        prep_result = self.prep_builder.build(raw)
        self.prep_cache.put(prep_result.prep)
        return {
            "artifact": "attach_task_file",
            "status": "ok",
            "task_id": task_key,
            "attachment_id": str(ready_attachment.attachment_id),
            "attachments_total": len(attachments),
            "prep_written": True,
        }

    def delete_attachment(self, *, task_id: str, attachment_id: str) -> dict[str, Any]:
        raw = self.raw_cache.get()
        if raw is None:
            raise UserError("Raw snapshot is unavailable.", code="raw_snapshot_unavailable")
        task_key = str(task_id or "").strip()
        if not task_key or task_key not in raw.tasks_by_id:
            raise UserError("Task was not found in current snapshot.", code="task_not_found")
        extra_snapshot = self.extra_store.get_snapshot()
        current = dict(extra_snapshot.items_by_task_id or {}).get(task_key)
        if current is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        attachments = [
            item
            for item in list(current.attachments or [])
            if str(item.attachment_id) != str(attachment_id or "").strip()
        ]
        if len(attachments) == len(list(current.attachments or [])):
            raise UserError("Attachment was not found.", code="attachment_not_found")
        items_by_task_id = dict(extra_snapshot.items_by_task_id)
        items_by_task_id[task_key] = TaskExtra(
            task_id=current.task_id,
            orphaned=bool(current.orphaned),
            updated_at_utc=datetime.now(timezone.utc),
            attachments=attachments,
            docs=list(current.docs),
            links=list(current.links),
            notes=str(current.notes),
            artifacts=list(current.artifacts),
        )
        self.extra_store.put_snapshot(
            ExtraSnapshot(
                version=max(int(extra_snapshot.version or 2), 1),
                updated_at_utc=datetime.now(timezone.utc),
                items_by_task_id=items_by_task_id,
            )
        )
        prep_result = self.prep_builder.build(raw)
        self.prep_cache.put(prep_result.prep)
        return {
            "artifact": "delete_task_attachment",
            "status": "ok",
            "task_id": task_key,
            "attachment_id": str(attachment_id or "").strip(),
            "attachments_total": len(attachments),
            "prep_written": True,
        }

    def cleanup_stale_attachments(
        self,
        *,
        ttl_seconds: int,
        delete_object: Any,
        now_utc: datetime | None = None,
    ) -> dict[str, Any]:
        now = now_utc or datetime.now(timezone.utc)
        ttl = max(int(ttl_seconds or 0), 1)
        stale_before = now.timestamp() - ttl
        extra_snapshot = self.extra_store.get_snapshot()
        items_by_task_id = dict(extra_snapshot.items_by_task_id or {})
        changed = False
        tasks_touched = 0
        warnings: list[str] = []
        counts = {
            ATTACHMENT_STATUS_PENDING_UPLOAD: 0,
            ATTACHMENT_STATUS_UPLOADED_UNVERIFIED: 0,
            ATTACHMENT_STATUS_DELETED: 0,
        }
        for task_id, current in list(items_by_task_id.items()):
            task_key = str(task_id or "").strip()
            if not task_key:
                continue
            current_attachments = list(current.attachments or [])
            kept_attachments: list[AttachmentMeta] = []
            task_changed = False
            for item in current_attachments:
                attachment_id = str(getattr(item, "attachment_id", "") or "").strip()
                item_task_id = str(getattr(item, "task_id", "") or "").strip()
                if not attachment_id or not item_task_id or item_task_id != task_key:
                    kept_attachments.append(item)
                    continue
                status = str(getattr(item, "status", "") or "").strip().lower()
                if status not in counts:
                    kept_attachments.append(item)
                    continue
                reference_time = self._cleanup_reference_time(item)
                if reference_time is None or reference_time.timestamp() >= stale_before:
                    kept_attachments.append(item)
                    continue
                storage_key = str(
                    getattr(item, "storage_key", "") or getattr(item, "key", "") or ""
                ).strip()
                if storage_key:
                    try:
                        delete_object(key=storage_key)
                    except AppError as error:
                        warnings.append(f"{task_key}:{attachment_id}:{error.code}")
                        kept_attachments.append(item)
                        continue
                counts[status] += 1
                task_changed = True
                changed = True
            if not task_changed:
                continue
            tasks_touched += 1
            items_by_task_id[task_key] = TaskExtra(
                task_id=current.task_id,
                orphaned=bool(current.orphaned),
                updated_at_utc=now,
                attachments=kept_attachments,
                docs=list(current.docs),
                links=list(current.links),
                notes=str(current.notes),
                artifacts=list(current.artifacts),
            )
        prep_written = False
        if changed:
            self.extra_store.put_snapshot(
                ExtraSnapshot(
                    version=max(int(extra_snapshot.version or 2), 1),
                    updated_at_utc=now,
                    items_by_task_id=items_by_task_id,
                )
            )
            raw = self.raw_cache.get()
            if raw is not None:
                prep_result = self.prep_builder.build(raw)
                self.prep_cache.put(prep_result.prep)
                prep_written = True
        return {
            "artifact": "cleanup_task_attachments",
            "status": "ok",
            "ttl_seconds": ttl,
            "pending_removed": counts[ATTACHMENT_STATUS_PENDING_UPLOAD],
            "uploaded_unverified_removed": counts[ATTACHMENT_STATUS_UPLOADED_UNVERIFIED],
            "deleted_removed": counts[ATTACHMENT_STATUS_DELETED],
            "tasks_touched": tasks_touched,
            "prep_written": prep_written,
            "warnings": warnings,
        }

    @staticmethod
    def _cleanup_reference_time(item: AttachmentMeta) -> datetime | None:
        status = str(getattr(item, "status", "") or "").strip().lower()
        if status == ATTACHMENT_STATUS_PENDING_UPLOAD:
            return getattr(item, "uploaded_at_utc", None)
        if status == ATTACHMENT_STATUS_UPLOADED_UNVERIFIED:
            return getattr(item, "verified_at_utc", None) or getattr(item, "uploaded_at_utc", None)
        if status == ATTACHMENT_STATUS_DELETED:
            return getattr(item, "deleted_at_utc", None)
        return None

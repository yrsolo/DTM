"""Snapshot engine domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class Window:
    start: date | None
    end: date | None
    mode: str = "intersects"


@dataclass(slots=True, frozen=True)
class Milestone:
    type: str
    planned: date | None = None
    actual: date | None = None
    status: str = "planned"


@dataclass(slots=True, frozen=True)
class AttachmentMeta:
    id: str
    key: str
    filename: str
    mime: str
    size: int
    uploaded_at_utc: datetime
    uploaded_by: str
    preview: str = ""
    task_id: str = ""
    attachment_id: str = ""
    filename_original: str = ""
    filename_display: str = ""
    mime_type: str = ""
    kind: str = ""
    size_bytes: int = 0
    storage_bucket: str = ""
    storage_key: str = ""
    storage_etag: str = ""
    storage_version: str = ""
    sha256: str = ""
    status: str = "ready"
    uploaded_by_user_id: str = ""
    verified_at_utc: datetime | None = None
    deleted_at_utc: datetime | None = None
    deleted_by_user_id: str = ""
    error_code: str = ""
    error_message: str = ""
    snapshot_visible: bool = True
    preview_capabilities: list[str] = field(default_factory=list)
    sort_key: str = ""
    summary_status: str = "none"
    summary_text: str = ""
    summary_model: str = ""
    summary_version: str = ""
    summary_generated_at_utc: datetime | None = None
    extracted_text_status: str = "none"
    extracted_text_ref: str = ""
    detected_language: str = ""
    page_count: int | None = None
    image_width: int | None = None
    image_height: int | None = None
    preview_state: str = "none"
    derived_preview_ref: str = ""
    classification: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    custom_meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.attachment_id:
            object.__setattr__(self, "attachment_id", str(self.id or "").strip())
        if not self.id:
            object.__setattr__(self, "id", str(self.attachment_id or "").strip())
        if not self.storage_key:
            object.__setattr__(self, "storage_key", str(self.key or "").strip())
        if not self.key:
            object.__setattr__(self, "key", str(self.storage_key or "").strip())
        if not self.filename_original:
            object.__setattr__(self, "filename_original", str(self.filename or "").strip())
        if not self.filename_display:
            object.__setattr__(self, "filename_display", str(self.filename or "").strip())
        if not self.filename:
            object.__setattr__(self, "filename", str(self.filename_display or self.filename_original or "").strip())
        if not self.mime_type:
            object.__setattr__(self, "mime_type", str(self.mime or "").strip())
        if not self.mime:
            object.__setattr__(self, "mime", str(self.mime_type or "").strip())
        if not self.size_bytes:
            object.__setattr__(self, "size_bytes", max(int(self.size or 0), 0))
        if not self.size:
            object.__setattr__(self, "size", max(int(self.size_bytes or 0), 0))
        if not self.uploaded_by_user_id:
            object.__setattr__(self, "uploaded_by_user_id", str(self.uploaded_by or "").strip())
        if not self.uploaded_by:
            object.__setattr__(self, "uploaded_by", str(self.uploaded_by_user_id or "").strip())
        if not self.sort_key:
            object.__setattr__(self, "sort_key", self.uploaded_at_utc.isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "attachment_id": str(self.attachment_id),
            "task_id": str(self.task_id),
            "filename_original": str(self.filename_original),
            "filename_display": str(self.filename_display),
            "mime_type": str(self.mime_type),
            "kind": str(self.kind),
            "size_bytes": int(self.size_bytes),
            "storage_bucket": str(self.storage_bucket),
            "storage_key": str(self.storage_key),
            "storage_etag": str(self.storage_etag),
            "storage_version": str(self.storage_version),
            "sha256": str(self.sha256),
            "status": str(self.status),
            "uploaded_by_user_id": str(self.uploaded_by_user_id),
            "uploaded_at_utc": self.uploaded_at_utc,
            "verified_at_utc": self.verified_at_utc,
            "deleted_at_utc": self.deleted_at_utc,
            "deleted_by_user_id": str(self.deleted_by_user_id),
            "error_code": str(self.error_code),
            "error_message": str(self.error_message),
            "snapshot_visible": bool(self.snapshot_visible),
            "preview_capabilities": list(self.preview_capabilities or []),
            "sort_key": str(self.sort_key),
            "preview": str(self.preview),
            "summary_status": str(self.summary_status),
            "summary_text": str(self.summary_text),
            "summary_model": str(self.summary_model),
            "summary_version": str(self.summary_version),
            "summary_generated_at_utc": self.summary_generated_at_utc,
            "extracted_text_status": str(self.extracted_text_status),
            "extracted_text_ref": str(self.extracted_text_ref),
            "detected_language": str(self.detected_language),
            "page_count": self.page_count,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "preview_state": str(self.preview_state),
            "derived_preview_ref": str(self.derived_preview_ref),
            "classification": dict(self.classification or {}),
            "tags": list(self.tags or []),
            "warnings": list(self.warnings or []),
            "custom_meta": dict(self.custom_meta or {}),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AttachmentMeta":
        return cls(
            id=str(payload.get("id", payload.get("attachment_id", ""))).strip(),
            key=str(payload.get("key", payload.get("storage_key", ""))).strip(),
            filename=str(payload.get("filename", payload.get("filename_display", payload.get("filename_original", "")))).strip(),
            mime=str(payload.get("mime", payload.get("mime_type", ""))).strip(),
            size=max(int(payload.get("size", payload.get("size_bytes", 0)) or 0), 0),
            uploaded_at_utc=payload.get("uploaded_at_utc"),
            uploaded_by=str(payload.get("uploaded_by", payload.get("uploaded_by_user_id", ""))).strip(),
            preview=str(payload.get("preview", "")).strip(),
            task_id=str(payload.get("task_id", "")).strip(),
            attachment_id=str(payload.get("attachment_id", payload.get("id", ""))).strip(),
            filename_original=str(payload.get("filename_original", payload.get("filename", ""))).strip(),
            filename_display=str(payload.get("filename_display", payload.get("filename", ""))).strip(),
            mime_type=str(payload.get("mime_type", payload.get("mime", ""))).strip(),
            kind=str(payload.get("kind", "")).strip(),
            size_bytes=max(int(payload.get("size_bytes", payload.get("size", 0)) or 0), 0),
            storage_bucket=str(payload.get("storage_bucket", "")).strip(),
            storage_key=str(payload.get("storage_key", payload.get("key", ""))).strip(),
            storage_etag=str(payload.get("storage_etag", "")).strip(),
            storage_version=str(payload.get("storage_version", "")).strip(),
            sha256=str(payload.get("sha256", "")).strip(),
            status=str(payload.get("status", "ready")).strip() or "ready",
            uploaded_by_user_id=str(payload.get("uploaded_by_user_id", payload.get("uploaded_by", ""))).strip(),
            verified_at_utc=payload.get("verified_at_utc"),
            deleted_at_utc=payload.get("deleted_at_utc"),
            deleted_by_user_id=str(payload.get("deleted_by_user_id", "")).strip(),
            error_code=str(payload.get("error_code", "")).strip(),
            error_message=str(payload.get("error_message", "")).strip(),
            snapshot_visible=bool(payload.get("snapshot_visible", True)),
            preview_capabilities=[str(item) for item in list(payload.get("preview_capabilities", []) or [])],
            sort_key=str(payload.get("sort_key", "")).strip(),
            summary_status=str(payload.get("summary_status", "none")).strip() or "none",
            summary_text=str(payload.get("summary_text", "")).strip(),
            summary_model=str(payload.get("summary_model", "")).strip(),
            summary_version=str(payload.get("summary_version", "")).strip(),
            summary_generated_at_utc=payload.get("summary_generated_at_utc"),
            extracted_text_status=str(payload.get("extracted_text_status", "none")).strip() or "none",
            extracted_text_ref=str(payload.get("extracted_text_ref", "")).strip(),
            detected_language=str(payload.get("detected_language", "")).strip(),
            page_count=payload.get("page_count"),
            image_width=payload.get("image_width"),
            image_height=payload.get("image_height"),
            preview_state=str(payload.get("preview_state", "none")).strip() or "none",
            derived_preview_ref=str(payload.get("derived_preview_ref", "")).strip(),
            classification=dict(payload.get("classification", {}) or {}),
            tags=[str(item) for item in list(payload.get("tags", []) or [])],
            warnings=[str(item) for item in list(payload.get("warnings", []) or [])],
            custom_meta=dict(payload.get("custom_meta", {}) or {}),
        )


@dataclass(slots=True, frozen=True)
class TaskSheet:
    task_id: str
    title: str
    owner_id: str
    group_id: str
    brand: str
    format_: str
    customer: str
    raw_timing: str
    status: str
    history: str
    # ISO date -> stage list
    timing: dict[str, list[str]] = field(default_factory=dict)
    milestones: list[Milestone] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class TaskExtra:
    task_id: str
    orphaned: bool = False
    updated_at_utc: datetime | None = None
    attachments: list[AttachmentMeta] = field(default_factory=list)
    docs: list[dict[str, Any]] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    notes: str = ""
    artifacts: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class ExtraSnapshot:
    version: int
    updated_at_utc: datetime
    items_by_task_id: dict[str, TaskExtra] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TaskView:
    sheet: TaskSheet
    extra: TaskExtra | None = None


@dataclass(slots=True, frozen=True)
class PersonView:
    name: str
    is_active: bool = True
    chat_id: str = ""
    vacation: str = ""
    position: str = ""
    person_id: str = ""
    contact_email: str = ""
    yandex_email: str = ""
    telegram: str = ""
    telegram_id: str = ""
    info: str = ""
    phone: str = ""
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PrepIndexes:
    by_status: dict[str, list[str]] = field(default_factory=dict)
    by_owner: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RawSnapshot:
    source_id: str
    source_hash: str
    fetched_at_utc: datetime
    tasks_by_id: dict[str, TaskSheet]


@dataclass(slots=True, frozen=True)
class PrepSnapshot:
    source_id: str
    raw_source_hash: str
    built_at_utc: datetime
    tasks_by_id: dict[str, TaskView]
    indexes: PrepIndexes = field(default_factory=PrepIndexes)


@dataclass(slots=True, frozen=True)
class PrepBuildResult:
    prep: PrepSnapshot
    timings_ms: dict[str, float] = field(default_factory=dict)
    extra_snapshot_changed: bool = False


@dataclass(slots=True, frozen=True)
class PeopleSnapshot:
    source_id: str
    fetched_at_utc: datetime
    people_by_name: dict[str, PersonView]


@dataclass(slots=True, frozen=True)
class SheetSnapshot:
    worksheet_range: str
    values: list[list[Any]]
    colors: list[Any]
    status_colors: list[Any] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class UpdateResult:
    source_id: str
    source_hash: str
    changed: bool
    fetched_at_utc: datetime
    raw_written: bool
    prep_written: bool
    timings_ms: dict[str, float] = field(default_factory=dict)

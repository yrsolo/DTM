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

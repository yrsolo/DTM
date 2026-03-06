"""Snapshot engine domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class Milestone:
    type: str
    planned: date | None = None
    actual: date | None = None
    status: str = "planned"


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
    docs: list[dict[str, Any]] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    notes: str = ""
    artifacts: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class TaskView:
    sheet: TaskSheet
    extra: TaskExtra | None = None


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
class SheetSnapshot:
    worksheet_range: str
    values: list[list[Any]]
    colors: list[Any]


@dataclass(slots=True, frozen=True)
class UpdateResult:
    source_id: str
    source_hash: str
    changed: bool
    fetched_at_utc: datetime
    raw_written: bool
    prep_written: bool

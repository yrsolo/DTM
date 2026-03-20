"""Contracts for the snapshot context."""

from dataclasses import dataclass
from datetime import date

from src.contexts.snapshot.internal.engine.model import AttachmentMeta, ExtraSnapshot, TaskExtra, TaskView, Window


@dataclass(frozen=True)
class SnapshotFrontendQuery:
    statuses: list[str]
    designer: str
    limit: int
    include_people: bool
    window_enabled: bool
    window_start: date | None
    window_end: date | None
    window_mode: str = "intersects"

__all__ = [
    "AttachmentMeta",
    "ExtraSnapshot",
    "SnapshotFrontendQuery",
    "TaskExtra",
    "TaskView",
    "Window",
]

from __future__ import annotations

from dataclasses import dataclass

from src.snapshot_engine.model import TaskView, Window


@dataclass(frozen=True)
class ReminderRequest:
    window: Window
    statuses: list[str] | None = None
    group_by_owner: bool = True
    limit_per_owner: int | None = None


@dataclass(frozen=True)
class ReminderGroup:
    owner_id: str
    tasks: list[TaskView]


@dataclass(frozen=True)
class ReminderResult:
    groups: list[ReminderGroup]

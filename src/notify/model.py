from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from src.snapshot_engine.model import TaskView


@dataclass(frozen=True)
class ReminderRequest:
    mode: str
    statuses: list[str] | None = None
    include_today: bool = True
    include_next_workday: bool = True
    today_override: date | None = None
    force_test_chat: bool = False
    test_chat_id_override: str = ""


@dataclass(frozen=True)
class ReminderGroup:
    owner_name: str
    tasks_today: list[TaskView]
    tasks_next_workday: list[TaskView]


@dataclass(frozen=True)
class ReminderDraft:
    owner_name: str
    text: str


@dataclass(frozen=True)
class ReminderResult:
    artifact: str = "reminder_v2"
    status: str = "ok"
    mode: str = "reminder_v2"
    today: str = ""
    next_workday: str = ""
    groups: list[ReminderGroup] = field(default_factory=list)
    drafts: dict[str, str] = field(default_factory=dict)
    messages: dict[str, str] = field(default_factory=dict)
    delivery_counters: dict[str, int] = field(default_factory=dict)
    enhancement_counters: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

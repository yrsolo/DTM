from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class JobResult:
    success: bool
    retryable: bool = False
    failure_kind: str = ""
    error_code: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    error: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class JobStatusRecord:
    job_id: str
    command_type: str
    status: str
    requested_at_utc: datetime
    started_at_utc: datetime | None = None
    finished_at_utc: datetime | None = None
    requested_by: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    retryable: bool = False
    error: dict[str, Any] | None = None

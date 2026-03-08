from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class RequestedBy:
    source: str
    user_id: str | None = None
    chat_id: str | None = None


@dataclass(frozen=True, slots=True)
class Command:
    job_id: str
    type: str
    created_at_utc: datetime
    requested_by: RequestedBy
    payload: dict[str, Any] = field(default_factory=dict)
    idempotency_key: str | None = None

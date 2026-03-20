from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GroupQueryRequest:
    mode: str
    statuses: list[str] | None = None
    include_today: bool = True
    include_next_workday: bool = True
    today_override: date | None = None

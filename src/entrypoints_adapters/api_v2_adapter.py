"""Adapter helpers for frontend v2 -> snapshot engine query."""

from __future__ import annotations

from datetime import date
from typing import Any

from src.snapshot_engine.engine import SnapshotFrontendQuery


def build_frontend_query(
    *,
    statuses: list[str],
    designer: str,
    limit: int,
    include_people: bool,
    window_data: dict[str, Any],
) -> SnapshotFrontendQuery:
    start = _parse_date(window_data.get("start"))
    end = _parse_date(window_data.get("end"))
    return SnapshotFrontendQuery(
        statuses=list(statuses),
        designer=str(designer).strip(),
        limit=int(limit),
        include_people=bool(include_people),
        window_enabled=bool(window_data.get("enabled", False)),
        window_start=start,
        window_end=end,
        window_mode=str(window_data.get("mode", "intersects") or "intersects"),
    )


def _parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None

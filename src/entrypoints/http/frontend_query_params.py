"""Frontend API query parsing helpers extracted from index entrypoint."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_statuses(raw: str) -> list[str]:
    items = [part.strip() for part in str(raw or "").split(",") if part.strip()]
    return items or ["work", "pre_done"]


def parse_limit(raw: str, default: int = 200) -> int:
    try:
        value = int(str(raw or default))
    except ValueError:
        value = default
    return max(1, min(value, 1000))


def parse_bool(raw: str, default: bool = True) -> bool:
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "y"}


def parse_window_query(params: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    window_start_raw = str(params.get("window_start", "")).strip()
    window_end_raw = str(params.get("window_end", "")).strip()
    window_mode = str(params.get("window_mode", "")).strip() or "intersects"

    if not window_start_raw and not window_end_raw:
        return (
            {
                "enabled": False,
                "start": None,
                "end": None,
                "mode": window_mode,
            },
            None,
        )

    if not window_start_raw or not window_end_raw:
        return {}, {
            "code": "invalid_window",
            "message": "Both window_start and window_end are required when window is enabled.",
            "details": {
                "window_start": window_start_raw or None,
                "window_end": window_end_raw or None,
            },
        }

    if window_mode != "intersects":
        return {}, {
            "code": "invalid_window",
            "message": "Unsupported window_mode. Allowed value: intersects.",
            "details": {"window_mode": window_mode},
        }

    try:
        window_start = datetime.strptime(window_start_raw, "%Y-%m-%d").date()
        window_end = datetime.strptime(window_end_raw, "%Y-%m-%d").date()
    except ValueError:
        return {}, {
            "code": "invalid_window",
            "message": "window_start/window_end must use YYYY-MM-DD format.",
            "details": {
                "window_start": window_start_raw,
                "window_end": window_end_raw,
            },
        }

    if window_start > window_end:
        return {}, {
            "code": "invalid_window",
            "message": "window_start must be less than or equal to window_end.",
            "details": {
                "window_start": window_start_raw,
                "window_end": window_end_raw,
            },
        }

    return (
        {
            "enabled": True,
            "start": window_start,
            "end": window_end,
            "mode": window_mode,
        },
        None,
    )

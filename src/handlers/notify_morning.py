"""Morning notification handler skeleton."""

from __future__ import annotations

from typing import Any


def handle_notify_morning(event: dict[str, Any]) -> dict[str, Any]:
    """Placeholder notify handler."""
    return {"status": "ok", "handler": "notify_morning", "event_received": bool(event)}


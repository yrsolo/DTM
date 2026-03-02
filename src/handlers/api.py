"""API handler skeleton."""

from __future__ import annotations

from typing import Any


def handle_api(event: dict[str, Any]) -> dict[str, Any]:
    """Placeholder API handler."""
    return {"status": "ok", "handler": "api", "event_received": bool(event)}


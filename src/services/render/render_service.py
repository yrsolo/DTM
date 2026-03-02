"""Render service skeleton."""

from __future__ import annotations

from typing import Any


def render_from_read_model(view_by_tasks: dict[str, Any]) -> dict[str, Any]:
    """Placeholder render result."""
    return {
        "artifact": "render_result",
        "rows": len(view_by_tasks.get("tasks", [])),
    }


"""Read-model builder skeleton."""

from __future__ import annotations

from typing import Any


def build_read_models(normalized_tasks: list[Any]) -> dict[str, Any]:
    """Build minimal read-model artifact placeholder."""
    return {
        "artifact": "read_models_v1",
        "items_total": len(normalized_tasks),
    }


"""Notifier adapter helpers over snapshot payload."""

from __future__ import annotations

from typing import Any


def extract_group_query_tasks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = payload.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    return [item for item in tasks if isinstance(item, dict)]

"""Read-model builder primitives."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable


def _task_get(task: Any, field: str, default: Any = None) -> Any:
    if isinstance(task, dict):
        return task.get(field, default)
    return getattr(task, field, default)


def _task_to_flat_row(task: Any) -> dict[str, Any]:
    return {
        "task_id": str(_task_get(task, "task_id", "")),
        "title": str(_task_get(task, "title", "")),
        "designer_id": _task_get(task, "designer_id"),
        "status": str(_task_get(task, "status", "")),
        "next_due_at": (
            _task_get(task, "next_due_at").isoformat()
            if hasattr(_task_get(task, "next_due_at"), "isoformat")
            else _task_get(task, "next_due_at")
        ),
    }


def build_read_models(normalized_tasks: Iterable[Any]) -> dict[str, Any]:
    """Build minimal v1 read models from normalized tasks."""
    tasks_rows = [_task_to_flat_row(task) for task in normalized_tasks]

    by_designer: dict[str, list[dict[str, Any]]] = {}
    for row in tasks_rows:
        designer_id = str(row.get("designer_id") or "unassigned")
        by_designer.setdefault(designer_id, []).append(
            {
                "task_id": row["task_id"],
                "title": row["title"],
                "status": row["status"],
                "next_due_at": row["next_due_at"],
            }
        )

    view_by_designer = []
    for designer_id, items in sorted(by_designer.items(), key=lambda item: item[0]):
        items_sorted = sorted(
            items,
            key=lambda task: (task.get("next_due_at") is None, task.get("next_due_at"), task["task_id"]),
        )
        view_by_designer.append(
            {
                "designer_id": designer_id,
                "tasks": items_sorted,
            }
        )

    generated_at_utc = datetime.now(timezone.utc).isoformat()
    return {
        "artifact": "read_models_v1",
        "generated_at_utc": generated_at_utc,
        "view_by_tasks": {
            "artifact": "view_by_tasks",
            "tasks": sorted(tasks_rows, key=lambda row: row["task_id"]),
        },
        "view_by_designer": {
            "artifact": "view_by_designer",
            "items": view_by_designer,
        },
        "summary": {
            "tasks_total": len(tasks_rows),
            "designers_total": len(view_by_designer),
        },
    }

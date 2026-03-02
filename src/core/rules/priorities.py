"""Priority and ordering rules for normalized tasks."""

from __future__ import annotations

from src.core.models.contracts import TaskNormalized


def sort_by_next_due(tasks: list[TaskNormalized]) -> list[TaskNormalized]:
    """Return tasks sorted by nearest due date then by task id."""
    return sorted(
        tasks,
        key=lambda task: (
            task.next_due_at is None,
            task.next_due_at,
            task.task_id,
        ),
    )


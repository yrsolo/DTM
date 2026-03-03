"""Shared query adapter over task query contract for API/render/notify consumers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from core.task_query_contract import TimeWindow, TaskProjection, apply_task_query, project_tasks


@dataclass(slots=True)
class TaskQueryContext:
    """Reusable projection context to avoid duplicated task projection logic."""

    projections: list[TaskProjection]


def build_task_query_context(tasks: Iterable[Any]) -> TaskQueryContext:
    """Project source tasks once and reuse across multiple query passes."""
    return TaskQueryContext(projections=project_tasks(tasks))


def query_projections(
    context: TaskQueryContext,
    *,
    statuses: Iterable[str] | None = None,
    designer: str = "",
    limit: int = 200,
    window: TimeWindow | None = None,
    milestone_types: Iterable[str] | None = None,
) -> list[TaskProjection]:
    """Apply unified query filters to projected tasks."""
    return apply_task_query(
        context.projections,
        statuses=statuses,
        designer=designer,
        limit=limit,
        window=window,
        milestone_types=milestone_types,
    )


def query_source_tasks(
    context: TaskQueryContext,
    *,
    statuses: Iterable[str] | None = None,
    designer: str = "",
    limit: int = 200,
    window: TimeWindow | None = None,
    milestone_types: Iterable[str] | None = None,
) -> list[Any]:
    """Return source tasks after applying unified query filters."""
    filtered = query_projections(
        context,
        statuses=statuses,
        designer=designer,
        limit=limit,
        window=window,
        milestone_types=milestone_types,
    )
    return [item.source_task for item in filtered if item.source_task is not None]

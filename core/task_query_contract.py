"""Unified task query contract shared by API, render, and reminder flows."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

import pandas as pd


def _to_str(value: Any) -> str:
    return str(value or "").strip()


@dataclass(slots=True, frozen=True)
class TimeWindow:
    start: date | None = None
    end: date | None = None
    mode: str = "intersects"

    @property
    def enabled(self) -> bool:
        return self.start is not None and self.end is not None


@dataclass(slots=True, frozen=True)
class MilestoneProjection:
    type: str
    label: str
    planned: date | None
    actual: date | None
    status: str


@dataclass(slots=True)
class TaskProjection:
    task_id: str
    title: str
    designer: str
    status: str
    color_status: str
    brand: str
    format_: str
    project_name: str
    customer: str
    raw_timing: str
    timing: dict[pd.Timestamp, list[str]]
    milestones: list[MilestoneProjection]
    source_task: Any | None = None

    @property
    def min_date(self) -> pd.Timestamp | None:
        return min(self.timing.keys()) if self.timing else None

    @property
    def max_date(self) -> pd.Timestamp | None:
        return max(self.timing.keys()) if self.timing else None

    @property
    def next_due(self) -> pd.Timestamp | None:
        today = pd.Timestamp.today().normalize()
        future_dates = [value for value in self.timing.keys() if value >= today]
        if future_dates:
            return min(future_dates)
        return self.max_date


def _normalize_milestone_type(stage_name: str) -> tuple[str, str]:
    value = _to_str(stage_name).lower()
    known_type_labels = {
        "start": "start",
        "storyboard": "storyboard",
        "animatic": "animatic",
        "prefinal": "prefinal",
        "final": "final",
        "onair": "onair",
        "feedback": "feedback",
        "draft": "draft",
    }
    if value in known_type_labels:
        return value, known_type_labels[value]
    mapping: list[tuple[str, str, str]] = [
        ("storyboard", "раскадров", "storyboard"),
        ("animatic", "анимат", "animatic"),
        ("prefinal", "префинал", "prefinal"),
        ("final", "финал", "final"),
        ("onair", "эфир", "onair"),
        ("feedback", "ответ", "feedback"),
        ("draft", "драфт", "draft"),
    ]
    for type_id, marker, label in mapping:
        if marker in value:
            return type_id, label
    compact = re.sub(r"\s+", " ", _to_str(stage_name)).strip()
    if compact:
        return f"stage_{hashlib.sha1(compact.encode('utf-8')).hexdigest()[:8]}", compact.lower()
    return "unknown_stage", "unknown_stage"


def _infer_milestone_status(stage_name: str) -> str:
    value = _to_str(stage_name).lower()
    if not value:
        return "unknown"
    if any(marker in value for marker in ("skip", "пропуск", "отмен", "не делаем")):
        return "skipped"
    if any(marker in value for marker in ("done", "готов", "сдан", "утвержд")):
        return "done"
    return "planned"


def _normalize_timing(raw_timing: Any) -> dict[pd.Timestamp, list[str]]:
    if not isinstance(raw_timing, dict):
        return {}
    normalized: dict[pd.Timestamp, list[str]] = {}
    for key, value in raw_timing.items():
        try:
            dt = pd.Timestamp(key)
        except Exception:
            continue
        stages = value if isinstance(value, list) else [value]
        normalized[dt] = [str(stage) for stage in stages]
    return normalized


def project_task(task: Any) -> TaskProjection:
    timing = _normalize_timing(getattr(task, "timing", {}))
    milestones: list[MilestoneProjection] = []
    for dt, stages in timing.items():
        planned = dt.date()
        for stage in stages:
            type_id, label = _normalize_milestone_type(str(stage))
            milestones.append(
                MilestoneProjection(
                    type=type_id,
                    label=label,
                    planned=planned,
                    actual=None,
                    status=_infer_milestone_status(str(stage)),
                )
            )
    milestones.sort(key=lambda item: (item.planned is None, item.planned or date.max, item.type))
    return TaskProjection(
        task_id=_to_str(getattr(task, "id", "")),
        title=_to_str(getattr(task, "name", "")),
        designer=_to_str(getattr(task, "designer", "")),
        status=_to_str(getattr(task, "status", "")),
        color_status=_to_str(getattr(task, "color_status", getattr(task, "status", ""))),
        brand=_to_str(getattr(task, "brand", "")),
        format_=_to_str(getattr(task, "format_", "")),
        project_name=_to_str(getattr(task, "project_name", "")),
        customer=_to_str(getattr(task, "customer", "")),
        raw_timing=_to_str(getattr(task, "raw_timing", "")),
        timing=timing,
        milestones=milestones,
        source_task=task,
    )


def project_tasks(tasks: Iterable[Any]) -> list[TaskProjection]:
    return [project_task(task) for task in tasks]


def _matches_designer(projection: TaskProjection, designer: str) -> bool:
    target = _to_str(designer).casefold()
    if not target:
        return True
    values = {_to_str(item).casefold() for item in projection.designer.split("\n") if _to_str(item)}
    return target in values


def _matches_status(projection: TaskProjection, statuses: set[str]) -> bool:
    if not statuses:
        return True
    return _to_str(projection.color_status).lower() in statuses


def _matches_window(projection: TaskProjection, window: TimeWindow) -> bool:
    if not window.enabled:
        return True
    if window.mode != "intersects":
        return False
    start = projection.min_date.date() if projection.min_date is not None else None
    end = projection.max_date.date() if projection.max_date is not None else None
    if start is not None and window.start <= start <= window.end:
        return True
    if end is not None and window.start <= end <= window.end:
        return True
    return False


def _matches_milestone_types(projection: TaskProjection, milestone_types: set[str]) -> bool:
    if not milestone_types:
        return True
    projection_types = {item.type for item in projection.milestones}
    return bool(projection_types.intersection(milestone_types))


def apply_task_query(
    projections: Iterable[TaskProjection],
    *,
    statuses: Iterable[str] | None = None,
    designer: str = "",
    limit: int = 200,
    window: TimeWindow | None = None,
    milestone_types: Iterable[str] | None = None,
) -> list[TaskProjection]:
    status_set = {str(item).strip().lower() for item in (statuses or []) if str(item).strip()}
    milestone_set = {str(item).strip().lower() for item in (milestone_types or []) if str(item).strip()}
    query_window = window or TimeWindow()
    items = list(projections)
    items = [
        item
        for item in items
        if _matches_status(item, status_set)
        and _matches_designer(item, designer)
        and _matches_window(item, query_window)
        and _matches_milestone_types(item, milestone_set)
    ]
    items.sort(key=lambda item: (item.next_due is None, item.next_due or pd.Timestamp.max, item.title))
    return items[: max(int(limit), 0)]


def query_source_tasks(
    tasks: Iterable[Any],
    *,
    statuses: Iterable[str] | None = None,
    designer: str = "",
    limit: int = 200,
    window: TimeWindow | None = None,
    milestone_types: Iterable[str] | None = None,
) -> list[Any]:
    projections = project_tasks(tasks)
    filtered = apply_task_query(
        projections,
        statuses=statuses,
        designer=designer,
        limit=limit,
        window=window,
        milestone_types=milestone_types,
    )
    return [item.source_task for item in filtered if item.source_task is not None]


def milestone_type_labels(projections: Iterable[TaskProjection]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for projection in projections:
        for milestone in projection.milestones:
            labels[milestone.type] = milestone.label
    return dict(sorted(labels.items()))


def group_by_designer(projections: Iterable[TaskProjection]) -> dict[str, list[TaskProjection]]:
    grouped: dict[str, list[TaskProjection]] = {}
    for projection in projections:
        key = projection.designer or "unassigned"
        grouped.setdefault(key, []).append(projection)
    return grouped


def milestones_in_window(projection: TaskProjection, window: TimeWindow) -> list[MilestoneProjection]:
    if not window.enabled:
        return list(projection.milestones)
    selected = []
    for milestone in projection.milestones:
        planned = milestone.planned
        if planned is not None and window.start <= planned <= window.end:
            selected.append(milestone)
    return selected

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from src.app.timezone_utils import format_sheet_timestamp, now_in_timezone, today_in_timezone
from src.contexts.snapshot.contracts import TaskView
from utils.func import GetColor

from .model import RenderCell, RenderPlan, RenderRequest


def _to_iso_date(value: str) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _task_date_bounds(task: TaskView) -> tuple[date | None, date | None]:
    dates: list[date] = []
    for key in dict(task.sheet.timing or {}).keys():
        parsed = _to_iso_date(key)
        if parsed is not None:
            dates.append(parsed)
    if not dates:
        return None, None
    dates.sort()
    return dates[0], dates[-1]


def _matches_status(task: TaskView, statuses: set[str]) -> bool:
    if not statuses:
        return True
    value = str(task.sheet.status or "").strip().lower()
    return value in statuses


def _matches_window(task: TaskView, req: RenderRequest) -> bool:
    if req.window is None or req.window.start is None or req.window.end is None:
        return True
    start, end = _task_date_bounds(task)
    if start is None and end is None:
        return False
    if start is None:
        start = end
    if end is None:
        end = start
    if start is None or end is None:
        return False
    return start <= req.window.end and end >= req.window.start


def _next_due(task: TaskView, timezone_name: str) -> date | None:
    today = today_in_timezone(timezone_name)
    dates: list[date] = []
    for key in dict(task.sheet.timing or {}).keys():
        parsed = _to_iso_date(key)
        if parsed is not None:
            dates.append(parsed)
    if not dates:
        return None
    future = [item for item in dates if item >= today]
    if future:
        return min(future)
    return max(dates)


@dataclass(frozen=True)
class _DesignerTask:
    owner: str
    task: TaskView


class DesignersRenderUseCase:
    """Build designers sheet plan with legacy-compatible layout."""

    def __init__(self, engine, timezone_name: str = "Europe/Moscow"):  # noqa: ANN001
        self._engine = engine
        self._color = GetColor()
        self._timezone_name = str(timezone_name or "Europe/Moscow").strip() or "Europe/Moscow"

    def _select_tasks(self, req: RenderRequest) -> list[_DesignerTask]:
        prep = self._engine.get_prep_snapshot()
        if prep is None:
            return []
        statuses = {
            str(item).strip().lower()
            for item in list(req.statuses or ["work", "pre_done"])
            if str(item).strip()
        }
        result: list[_DesignerTask] = []
        for view in prep.tasks_by_id.values():
            owner = str(view.sheet.owner_id or "").strip()
            if not owner:
                continue
            if not _matches_status(view, statuses):
                continue
            if not _matches_window(view, req):
                continue
            result.append(_DesignerTask(owner=owner, task=view))
        result.sort(
            key=lambda item: (
                _next_due(item.task, self._timezone_name) is None,
                _next_due(item.task, self._timezone_name) or date.max,
                str(item.task.sheet.title or ""),
            )
        )
        return result

    def build_plan(self, req: RenderRequest) -> RenderPlan:
        selected = self._select_tasks(req)
        if not selected:
            prep = self._engine.get_prep_snapshot()
            warning = "prep_snapshot_missing" if prep is None else "empty_render_plan"
            return RenderPlan(values=[], borders=[], warnings=[warning])

        by_owner: dict[str, list[TaskView]] = {}
        owners: set[str] = set()
        for item in selected:
            owners.add(item.owner)
            by_owner.setdefault(item.owner, []).append(item.task)

        values: list[RenderCell] = []
        start_row = 2
        row = start_row + 1
        col = 2
        for owner in sorted(owners):
            owner_tasks = by_owner.get(owner, [])
            if not owner_tasks:
                continue
            values.append(
                RenderCell(
                    row=start_row,
                    col=col,
                    value=owner,
                    color="#9F65CC",
                    text_color="#FFFFFF",
                    bold=True,
                    font_size=12,
                )
            )
            for task in owner_tasks:
                note = f"{task.sheet.customer}\n{task.sheet.raw_timing}"
                values.append(
                    RenderCell(
                        row=row,
                        col=col,
                        value=str(task.sheet.title or ""),
                        note=note,
                    )
                )
                row += 1
            col += 1
            row = start_row + 1

        values.append(
            RenderCell(
                row=1,
                col=1,
                value=format_sheet_timestamp(now_in_timezone(self._timezone_name)),
            )
        )
        return RenderPlan(values=values, borders=[], warnings=[])

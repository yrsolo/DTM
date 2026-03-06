from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.snapshot_engine.engine import SnapshotEngine
from src.snapshot_engine.model import TaskView

from .model import RenderPlan, RenderRequest
from .model import RenderCell


@dataclass(frozen=True)
class _TaskRange:
    start: date | None
    end: date | None


def _task_range(task: TaskView) -> _TaskRange:
    all_dates: list[date] = []
    for key in dict(task.sheet.timing or {}).keys():
        text = str(key or "").strip()
        if not text:
            continue
        try:
            all_dates.append(date.fromisoformat(text[:10]))
        except ValueError:
            continue
    for milestone in list(task.sheet.milestones or []):
        if milestone.planned is not None:
            all_dates.append(milestone.planned)
        if milestone.actual is not None:
            all_dates.append(milestone.actual)
    if not all_dates:
        return _TaskRange(start=None, end=None)
    ordered = sorted(all_dates)
    return _TaskRange(start=ordered[0], end=ordered[-1])


def _matches_window(task: TaskView, req: RenderRequest) -> bool:
    if req.window is None or req.window.start is None or req.window.end is None:
        return True
    tr = _task_range(task)
    if tr.start is None and tr.end is None:
        return False
    start = tr.start or tr.end
    end = tr.end or tr.start
    if start is None or end is None:
        return False
    return start <= req.window.end and end >= req.window.start


class RenderUseCase:
    """Pure transformation: snapshot query result into render plan."""

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine

    def build_plan(self, req: RenderRequest) -> RenderPlan:
        prep = self._engine.get_prep_snapshot()
        if prep is None:
            return RenderPlan(values=[], formats=[], warnings=["prep_snapshot_missing"])

        statuses = {
            str(item).strip().lower()
            for item in list(req.statuses or ["work", "pre_done"])
            if str(item).strip()
        }
        selected: list[TaskView] = []
        for view in prep.tasks_by_id.values():
            status = str(view.sheet.status or "").strip().lower()
            if statuses and status not in statuses:
                continue
            if not _matches_window(view, req):
                continue
            selected.append(view)

        if not selected:
            return RenderPlan(values=[], formats=[], warnings=["empty_render_plan"])

        selected.sort(
            key=lambda item: (
                _task_range(item).end or date.min,
                str(item.sheet.owner_id),
                str(item.sheet.task_id),
            ),
            reverse=True,
        )

        cells: list[RenderCell] = []
        headers = ["id", "title", "ownerId", "groupId", "status", "dateEnd", "history"]
        for idx, header in enumerate(headers, start=1):
            cells.append(RenderCell(row=1, col=idx, value=header))

        row_idx = 2
        for task in selected:
            end_date = _task_range(task).end
            row_values = [
                task.sheet.task_id,
                task.sheet.title,
                task.sheet.owner_id,
                task.sheet.group_id,
                task.sheet.status,
                end_date.isoformat() if end_date is not None else "",
                task.sheet.history,
            ]
            for col_idx, value in enumerate(row_values, start=1):
                cells.append(RenderCell(row=row_idx, col=col_idx, value=str(value or "")))
            row_idx += 1

        return RenderPlan(values=cells, formats=[], warnings=[])

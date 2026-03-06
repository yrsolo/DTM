from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.snapshot_engine.engine import SnapshotEngine
from src.snapshot_engine.model import TaskView

from .model import ReminderGroup, ReminderRequest, ReminderResult


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


def _matches_window(task: TaskView, req: ReminderRequest) -> bool:
    if req.window.start is None or req.window.end is None:
        return True
    tr = _task_range(task)
    if tr.start is None and tr.end is None:
        return False
    start = tr.start or tr.end
    end = tr.end or tr.start
    if start is None or end is None:
        return False
    return start <= req.window.end and end >= req.window.start


class ReminderUseCase:
    """Pure selection + grouping. Does not format or send."""

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine

    def run(self, req: ReminderRequest) -> ReminderResult:
        prep = self._engine.get_prep_snapshot()
        if prep is None:
            return ReminderResult(groups=[])
        statuses = {str(item).strip().lower() for item in list(req.statuses or ["work", "pre_done"]) if str(item).strip()}
        selected: list[TaskView] = []
        for view in prep.tasks_by_id.values():
            status = str(view.sheet.status or "").strip().lower()
            if statuses and status not in statuses:
                continue
            if not _matches_window(view, req):
                continue
            selected.append(view)
        selected.sort(key=lambda item: (str(item.sheet.owner_id), str(item.sheet.task_id)))

        groups: dict[str, list[TaskView]] = {}
        for view in selected:
            owner = str(view.sheet.owner_id).strip() or "unassigned"
            groups.setdefault(owner, []).append(view)

        result_groups: list[ReminderGroup] = []
        for owner_id, tasks in groups.items():
            items = list(tasks)
            if req.limit_per_owner is not None and req.limit_per_owner > 0:
                items = items[: int(req.limit_per_owner)]
            result_groups.append(ReminderGroup(owner_id=owner_id, tasks=items))
        result_groups.sort(key=lambda item: str(item.owner_id))
        return ReminderResult(groups=result_groups)

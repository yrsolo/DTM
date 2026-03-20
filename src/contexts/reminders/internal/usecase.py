from __future__ import annotations

from datetime import date, datetime, timedelta

from src.contexts.snapshot.contracts import TaskView

from .model import ReminderGroup, ReminderRequest


def normalize_person_name(value: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    return " ".join(text.split())


def next_workday(today: date) -> date:
    weekday = today.weekday()
    if weekday == 4:
        return today + timedelta(days=3)
    if weekday == 5:
        return today + timedelta(days=2)
    return today + timedelta(days=1)


def _milestone_days(task: TaskView) -> set[date]:
    days: set[date] = set()
    for milestone in list(task.sheet.milestones or []):
        day = milestone.planned or milestone.actual
        if day is not None:
            days.add(day)
    return days


class ReminderUseCase:
    def __init__(self, prep_snapshot_source):  # noqa: ANN001
        if callable(prep_snapshot_source):
            self._load_prep_snapshot = prep_snapshot_source
        else:
            getter = getattr(prep_snapshot_source, "get_prep_snapshot", None)
            self._load_prep_snapshot = getter if callable(getter) else (lambda: None)

    def select(self, req: ReminderRequest) -> tuple[list[ReminderGroup], date, date]:
        prep = self._load_prep_snapshot()
        if prep is None:
            today = req.today_override or datetime.now().date()
            return [], today, next_workday(today)

        today = req.today_override or datetime.now().date()
        next_day = next_workday(today)
        statuses = {
            str(item).strip().lower()
            for item in list(req.statuses or ["work", "pre_done"])
            if str(item).strip()
        }
        tasks_today: dict[str, list[TaskView]] = {}
        tasks_next: dict[str, list[TaskView]] = {}
        for task in prep.tasks_by_id.values():
            status = str(task.sheet.status or "").strip().lower()
            if statuses and status not in statuses:
                continue
            milestone_days = _milestone_days(task)
            if not milestone_days:
                continue
            owner = str(task.sheet.owner_id or "").strip()
            if not owner:
                continue
            if req.include_today and today in milestone_days:
                tasks_today.setdefault(owner, []).append(task)
            if req.include_next_workday and next_day in milestone_days:
                tasks_next.setdefault(owner, []).append(task)

        owners = sorted(set(tasks_today.keys()) | set(tasks_next.keys()))
        groups: list[ReminderGroup] = []
        for owner in owners:
            today_items = sorted(tasks_today.get(owner, []), key=lambda item: (str(item.sheet.brand), str(item.sheet.title), str(item.sheet.task_id)))
            next_items = sorted(tasks_next.get(owner, []), key=lambda item: (str(item.sheet.brand), str(item.sheet.title), str(item.sheet.task_id)))
            groups.append(ReminderGroup(owner_name=owner, tasks_today=today_items, tasks_next_workday=next_items))
        return groups, today, next_day

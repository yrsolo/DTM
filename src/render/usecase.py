from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable

from src.snapshot_engine.engine import SnapshotEngine
from src.snapshot_engine.model import TaskView
from utils.func import GetColor, RGBColor

from .model import RenderBorder, RenderCell, RenderPlan, RenderRequest


def _parse_date(value: str) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _task_dates(task: TaskView) -> list[date]:
    dates: list[date] = []
    for key in dict(task.sheet.timing or {}).keys():
        parsed = _parse_date(key)
        if parsed is not None:
            dates.append(parsed)
    for milestone in list(task.sheet.milestones or []):
        if milestone.planned is not None:
            dates.append(milestone.planned)
        if milestone.actual is not None:
            dates.append(milestone.actual)
    return sorted(set(dates))


def _task_stage_for_day(task: TaskView, day: date) -> str:
    stage_items = list(dict(task.sheet.timing or {}).get(day.isoformat(), []))
    if not stage_items:
        return ""
    return ", ".join(str(item) for item in stage_items if str(item).strip())


def _matches_window(task: TaskView, req: RenderRequest) -> bool:
    if req.window is None or req.window.start is None or req.window.end is None:
        return True
    dates = _task_dates(task)
    if not dates:
        return False
    start = dates[0]
    end = dates[-1]
    return start <= req.window.end and end >= req.window.start


def _as_hex(color: RGBColor) -> str:
    return f"#{str(color)}"


@dataclass(frozen=True)
class _TaskTimeline:
    task: TaskView
    min_date: date
    max_date: date


def _iter_days(start: date, end: date) -> Iterable[date]:
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def _iter_days_half_open(start: date, end_exclusive: date) -> Iterable[date]:
    day = start
    while day < end_exclusive:
        yield day
        day += timedelta(days=1)


class RenderUseCase:
    """Build Gantt-like render plan from snapshot tasks."""

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine
        self._color = GetColor()

    def _window_bounds(self, req: RenderRequest) -> tuple[date, date, date]:
        today = date.today()
        if req.window is not None and req.window.start is not None and req.window.end is not None:
            start = req.window.start
            end = req.window.end
            if end < start:
                start, end = end, start
            return start, end, today
        return today - timedelta(days=5), today + timedelta(days=150), today

    def build_plan(self, req: RenderRequest) -> RenderPlan:
        prep = self._engine.get_prep_snapshot()
        if prep is None:
            return RenderPlan(values=[], borders=[], warnings=["prep_snapshot_missing"])

        statuses = {
            str(item).strip().lower()
            for item in list(req.statuses or ["work", "pre_done", "wait"])
            if str(item).strip()
        }
        by_owner: dict[str, list[_TaskTimeline]] = {}
        for view in prep.tasks_by_id.values():
            status = str(view.sheet.status or "").strip().lower()
            if statuses and status not in statuses:
                continue
            if not _matches_window(view, req):
                continue
            dates = _task_dates(view)
            if not dates:
                continue
            owner = str(view.sheet.owner_id or "").strip() or "[Не назначен]"
            by_owner.setdefault(owner, []).append(
                _TaskTimeline(task=view, min_date=dates[0], max_date=dates[-1])
            )

        if not by_owner:
            return RenderPlan(values=[], borders=[], warnings=["empty_render_plan"])

        start, end, today = self._window_bounds(req)
        values: list[RenderCell] = []
        row = 2

        for owner in sorted(by_owner.keys()):
            owner_tasks = sorted(by_owner[owner], key=lambda item: item.min_date)
            base_color = self._color()
            timeline_base = self._color("gray")

            # Per-owner timeline row.
            col = 2
            for day in _iter_days_half_open(start, end):
                if day.weekday() >= 5:
                    day_color = (timeline_base if day != today else self._color("green")) ** 0.25
                else:
                    day_color = timeline_base if day != today else self._color("green")
                values.append(
                    RenderCell(
                        row=row,
                        col=col,
                        value=day.strftime("%d.%m"),
                        color=_as_hex(day_color),
                        text_color=_as_hex(timeline_base**3),
                        bold=True,
                        italic=True,
                        font_size=9,
                    )
                )
                col += 1

            values.append(
                RenderCell(
                    row=row,
                    col=1,
                    value=owner,
                    color=_as_hex(base_color**1.5),
                    text_color=_as_hex(base_color**0.03),
                    bold=True,
                    font_size=10,
                )
            )
            row += 1

            total = max(1, len(owner_tasks))
            for index, timeline in enumerate(owner_tasks):
                task = timeline.task
                emphasis = 1 if total == 1 else 0.5 + 1.5 * (total - index) / total
                task_color = base_color**emphasis
                note = (
                    f"Менеджер: {task.sheet.customer}\n"
                    f"Статус:\n{task.sheet.history}\n"
                    f"Тайминг:\n{task.sheet.raw_timing}"
                )
                values.append(
                    RenderCell(
                        row=row,
                        col=1,
                        value=task.sheet.title,
                        note=note,
                        font_size=9,
                    )
                )

                task_start = timeline.min_date if timeline.min_date > start else start
                task_end = timeline.max_date if timeline.max_date < end else end
                col = 2 + (task_start - start).days
                for day in _iter_days(task_start, task_end):
                    stage = _task_stage_for_day(task, day)
                    if day.weekday() >= 5:
                        stage_color = (
                            task_color
                            if str(task.sheet.status or "").strip().lower() not in {"wait"}
                            else task_color.gray
                        ) ** 0.6
                    else:
                        stage_color = (
                            task_color
                            if str(task.sheet.status or "").strip().lower() not in {"wait"}
                            else task_color.gray
                        )
                    values.append(
                        RenderCell(
                            row=row,
                            col=col,
                            value=stage[:5].upper(),
                            note=f"{stage} \n{task.sheet.title}" if stage else "",
                            color=_as_hex(stage_color),
                            text_color=_as_hex(task_color**0.01),
                            bold=True,
                            font_size=8,
                        )
                    )
                    col += 1
                row += 1

        values.append(
            RenderCell(
                row=1,
                col=1,
                value=datetime.now().strftime("%H:%M %B %d"),
                bold=True,
            )
        )
        borders = [
            RenderBorder(
                worksheet_range="G1:H50",
                side="left",
                width=3,
                color="#5FAD56",
            )
        ]
        return RenderPlan(values=values, borders=borders, warnings=[])

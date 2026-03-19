from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .group_query_usecase import ReminderGroup, normalize_person_name


@dataclass(frozen=True)
class GroupQueryFormatter:
    def _stage_preview(self, task, day: date) -> str:  # noqa: ANN001
        stages = [str(item).strip() for item in list(task.sheet.timing.get(day.isoformat(), [])) if str(item).strip()]
        if not stages:
            return "этап не указан"
        return ", ".join(stages[:2])

    def _flatten(self, groups: list[ReminderGroup], *, today: date, next_workday: date) -> list[tuple[date, object, str]]:
        rows: list[tuple[date, object, str]] = []
        for group in list(groups or []):
            for task in list(group.tasks_today or []):
                rows.append((today, task, group.owner_name))
            for task in list(group.tasks_next_workday or []):
                rows.append((next_workday, task, group.owner_name))
        rows.sort(key=lambda item: (item[0], str(item[1].sheet.brand), str(item[1].sheet.title), str(item[1].sheet.task_id)))
        return rows

    def build_tasks_reply(self, groups: list[ReminderGroup], *, requester_name: str, today: date, next_workday: date) -> str:
        target = normalize_person_name(requester_name)
        selected = next((group for group in list(groups or []) if normalize_person_name(group.owner_name) == target), None)
        if selected is None or (not selected.tasks_today and not selected.tasks_next_workday):
            return f"@{requester_name}, не вижу задач с milestone на сегодня или следующий рабочий день."
        lines = [f"@{requester_name}, ближайшие задачи по вашим milestone:"]
        idx = 1
        for day, tasks in ((today, list(selected.tasks_today or [])), (next_workday, list(selected.tasks_next_workday or []))):
            for task in tasks:
                lines.append(f"{idx}. {day.strftime('%d.%m')} - {task.sheet.title} ({self._stage_preview(task, day)})")
                idx += 1
        return "\n".join(lines)

    def build_deadlines_reply(self, groups: list[ReminderGroup], *, today: date, next_workday: date) -> str:
        rows = self._flatten(groups, today=today, next_workday=next_workday)
        if not rows:
            return "Ближайших milestone на сегодня и следующий рабочий день не найдено."
        preview = rows[:10]
        lines = ["Ближайшие milestone по команде:"]
        for idx, (day, task, owner_name) in enumerate(preview, start=1):
            lines.append(f"{idx}. {day.strftime('%d.%m')} - {task.sheet.title} [{owner_name}] ({self._stage_preview(task, day)})")
        if len(rows) > len(preview):
            lines.append(f"... и еще {len(rows) - len(preview)} задач.")
        return "\n".join(lines)

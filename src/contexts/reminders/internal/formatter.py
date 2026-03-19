from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from .model import ReminderDraft, ReminderGroup


def _filter_stages(stages: list[str], hidden_words: list[str]) -> list[str]:
    forbidden = [str(word).strip().lower() for word in list(hidden_words or []) if str(word).strip()]
    result: list[str] = []
    for stage in list(stages or []):
        stage_text = str(stage or "").strip()
        if not stage_text:
            continue
        stage_lower = stage_text.lower()
        if any(token in stage_lower for token in forbidden):
            continue
        result.append(stage_text)
    return result


@dataclass(frozen=True)
class ReminderFormatter:
    timezone_name: str = "Europe/Moscow"
    hidden_stage_names: tuple[str, ...] = ()

    def _day_lines(self, tasks: list, day: date) -> list[str]:
        lines: list[str] = []
        idx = 1
        iso = day.isoformat()
        for task in tasks:
            stages = _filter_stages(list(task.sheet.timing.get(iso, [])), list(self.hidden_stage_names))
            if not stages:
                continue
            format_text = str(task.sheet.format_ or "").split("\n")[0].strip()
            project_name = str(task.sheet.group_id or "").strip()
            brand = str(task.sheet.brand or "").strip()
            lines.append(f"{idx}. {brand} // {format_text} // для проекта «{project_name}» - сдаём «{', '.join(stages)}»")
            idx += 1
        return lines

    def build_draft(self, group: ReminderGroup, *, today: date, next_workday: date) -> ReminderDraft | None:
        now = datetime.now(ZoneInfo(self.timezone_name))
        intro = f"Привет {group.owner_name}! Сегодня {now.strftime('%A, %d.%m')} в {now.strftime('%H:%M')}."
        message = intro
        today_lines = self._day_lines(group.tasks_today, today)
        if today_lines:
            message += "\n\nЗадачи на сегодня:\n" + "\n".join(today_lines)
        next_lines = self._day_lines(group.tasks_next_workday, next_workday)
        if next_lines:
            message += f"\n\nЗадачи на {next_workday.strftime('%A, %d.%m')}:\n" + "\n".join(next_lines)
        if message == intro:
            return None
        return ReminderDraft(owner_name=group.owner_name, text=message)

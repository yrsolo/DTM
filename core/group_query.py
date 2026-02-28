"""Group-chat query parsing and response rendering for Telegram mentions/commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd

from core.repository import Task


SUPPORTED_CHAT_TYPES = frozenset({"group", "supergroup"})
TASK_COMMANDS = ("/tasks", "/задачи")
DEADLINE_COMMANDS = ("/deadlines", "/дедлайны")


@dataclass(frozen=True)
class GroupQueryRequest:
    """Parsed group query request extracted from Telegram update payload."""

    chat_id: int | str
    requester_name: str
    action: str  # "tasks" | "deadlines"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_spaces(value: str) -> str:
    return " ".join(value.split())


def _requester_name(message_from: dict[str, Any]) -> str:
    first_name = _normalize_text(message_from.get("first_name"))
    last_name = _normalize_text(message_from.get("last_name"))
    full = _normalize_spaces(f"{first_name} {last_name}")
    if full:
        return full
    username = _normalize_text(message_from.get("username"))
    if username:
        return username
    return "дизайнер"


def _contains_bot_mention(text: str, bot_username: str) -> bool:
    username = _normalize_text(bot_username).lstrip("@").lower()
    if not username:
        return False
    return f"@{username}" in text.lower()


def _resolve_action(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("дедлайн", "срок", "deadline")):
        return "deadlines"
    return "tasks"


def _match_bot_command(text: str, bot_username: str) -> str | None:
    command = text.split(" ", 1)[0].strip()
    if not command.startswith("/"):
        return None

    base, _, suffix = command.partition("@")
    username = _normalize_text(bot_username).lstrip("@").lower()
    if suffix and username and suffix.lower() != username:
        return None

    if base.lower() in TASK_COMMANDS:
        return "tasks"
    if base.lower() in DEADLINE_COMMANDS:
        return "deadlines"
    return None


def parse_group_query_request(update: dict[str, Any], bot_username: str = "") -> GroupQueryRequest | None:
    """Return query request when update asks bot for tasks/deadlines in group chat."""

    message = update.get("message")
    if not isinstance(message, dict):
        return None

    chat = message.get("chat") or {}
    if chat.get("type") not in SUPPORTED_CHAT_TYPES:
        return None
    chat_id = chat.get("id")
    text = _normalize_text(message.get("text"))
    if not chat_id or not text:
        return None

    command_action = _match_bot_command(text, bot_username)
    if command_action:
        requester = _requester_name(message.get("from") or {})
        return GroupQueryRequest(chat_id=chat_id, requester_name=requester, action=command_action)

    if _contains_bot_mention(text, bot_username):
        requester = _requester_name(message.get("from") or {})
        action = _resolve_action(text)
        return GroupQueryRequest(chat_id=chat_id, requester_name=requester, action=action)
    return None


def _task_due_date(task: Task, today: pd.Timestamp) -> pd.Timestamp | None:
    future_dates = [date for date in task.timing.keys() if date >= today]
    if future_dates:
        return min(future_dates)
    return task.max_date


def _task_matches_designer(task: Task, designer_name: str) -> bool:
    target = _normalize_text(designer_name).casefold()
    if not target:
        return False
    values = [
        _normalize_text(item).casefold()
        for item in str(task.designer or "").split("\n")
        if _normalize_text(item)
    ]
    return target in values


def _task_stage_preview(task: Task, date: pd.Timestamp) -> str:
    stages = task.timing.get(date, [])
    if not stages:
        return "этап не указан"
    return ", ".join(str(stage) for stage in stages[:2])


def build_tasks_reply(tasks: Iterable[Task], requester_name: str, today: pd.Timestamp | None = None) -> str:
    """Build response with current tasks for one designer."""

    now = (today or pd.Timestamp.today()).normalize()
    matched = [task for task in tasks if _task_matches_designer(task, requester_name)]
    if not matched:
        return f"@{requester_name}, не вижу активных задач на ваше имя."

    rows: list[tuple[pd.Timestamp, Task]] = []
    for task in matched:
        due_date = _task_due_date(task, now)
        if due_date is not None:
            rows.append((due_date, task))
    rows.sort(key=lambda item: item[0])
    preview = rows[:7]

    lines = [f"@{requester_name}, ваши ближайшие задачи:"]
    for idx, (due_date, task) in enumerate(preview, start=1):
        date_str = due_date.strftime("%d.%m")
        stage = _task_stage_preview(task, due_date)
        lines.append(f"{idx}. {date_str} - {task.name} ({stage})")
    if len(rows) > len(preview):
        lines.append(f"... и еще {len(rows) - len(preview)} задач.")
    return "\n".join(lines)


def build_deadlines_reply(tasks: Iterable[Task], today: pd.Timestamp | None = None) -> str:
    """Build response with nearest deadlines across all active tasks."""

    now = (today or pd.Timestamp.today()).normalize()
    rows: list[tuple[pd.Timestamp, Task]] = []
    for task in tasks:
        due_date = _task_due_date(task, now)
        if due_date is not None:
            rows.append((due_date, task))
    if not rows:
        return "Ближайших дедлайнов не найдено."

    rows.sort(key=lambda item: item[0])
    preview = rows[:10]
    lines = ["Ближайшие дедлайны по команде:"]
    for idx, (due_date, task) in enumerate(preview, start=1):
        date_str = due_date.strftime("%d.%m")
        stage = _task_stage_preview(task, due_date)
        lines.append(f"{idx}. {date_str} - {task.name} [{task.designer}] ({stage})")
    if len(rows) > len(preview):
        lines.append(f"... и еще {len(rows) - len(preview)} задач.")
    return "\n".join(lines)

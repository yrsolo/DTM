"""Group-query HTTP handler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd

from src.adapters.telegram import TelegramNotifier
from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.response_utils import json_response
from src.entrypoints_adapters.api_v2_adapter import build_frontend_query
from src.snapshot_engine import build_snapshot_engine

SUPPORTED_CHAT_TYPES = frozenset({"group", "supergroup"})
TASK_COMMANDS = ("/tasks", "/задачи")
DEADLINE_COMMANDS = ("/deadlines", "/дедлайны")


@dataclass(slots=True)
class _GroupTaskProjection:
    name: str
    designer: str
    timing: dict[pd.Timestamp, list[str]]

    @property
    def max_date(self) -> pd.Timestamp | None:
        return max(self.timing.keys()) if self.timing else None


@dataclass(slots=True, frozen=True)
class _GroupQueryRequest:
    chat_id: int | str
    requester_name: str
    action: str


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_spaces(value: str) -> str:
    return " ".join(value.split())


def _requester_name(message_from: dict[str, Any]) -> str:
    first_name = _normalize_text(message_from.get("first_name"))
    last_name = _normalize_text(message_from.get("last_name"))
    full_name = _normalize_spaces(f"{first_name} {last_name}")
    if full_name:
        return full_name
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


def _parse_group_query_request(update: dict[str, Any], *, bot_username: str = "") -> _GroupQueryRequest | None:
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
    action = _match_bot_command(text, bot_username)
    if action:
        return _GroupQueryRequest(
            chat_id=chat_id,
            requester_name=_requester_name(message.get("from") or {}),
            action=action,
        )
    if _contains_bot_mention(text, bot_username):
        return _GroupQueryRequest(
            chat_id=chat_id,
            requester_name=_requester_name(message.get("from") or {}),
            action=_resolve_action(text),
        )
    return None


def _parse_iso_day(value: str) -> pd.Timestamp | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return pd.Timestamp(datetime.fromisoformat(text[:10]))
    except Exception:
        return None


def _group_tasks_from_payload(payload: dict[str, Any]) -> list[_GroupTaskProjection]:
    people = payload.get("entities", {}).get("people", [])
    owner_map: dict[str, str] = {}
    for person in people if isinstance(people, list) else []:
        if not isinstance(person, dict):
            continue
        person_id = str(person.get("id", "")).strip()
        person_name = str(person.get("name", "")).strip()
        if person_id:
            owner_map[person_id] = person_name

    result: list[_GroupTaskProjection] = []
    tasks = payload.get("tasks", [])
    for task in tasks if isinstance(tasks, list) else []:
        if not isinstance(task, dict):
            continue
        designer = owner_map.get(str(task.get("ownerId", "")).strip(), "")
        timing: dict[pd.Timestamp, list[str]] = {}
        milestones = task.get("milestones", [])
        for milestone in milestones if isinstance(milestones, list) else []:
            if not isinstance(milestone, dict):
                continue
            when = _parse_iso_day(str(milestone.get("planned", "")))
            if when is None:
                continue
            stage = str(milestone.get("type", "")).strip()
            if not stage:
                continue
            timing.setdefault(when, []).append(stage)
        if not timing:
            fallback = _parse_iso_day(str(task.get("date", {}).get("end", "")))
            if fallback is not None:
                timing[fallback] = ["stage"]
        result.append(
            _GroupTaskProjection(
                name=str(task.get("title", "")).strip(),
                designer=designer,
                timing=timing,
            )
        )
    return result


def _task_due_date(task: _GroupTaskProjection, today: pd.Timestamp) -> pd.Timestamp | None:
    future_dates = [day for day in task.timing.keys() if day >= today]
    if future_dates:
        return min(future_dates)
    return task.max_date


def _task_matches_designer(task: _GroupTaskProjection, designer_name: str) -> bool:
    target = _normalize_text(designer_name).casefold()
    if not target:
        return False
    values = [
        _normalize_text(item).casefold()
        for item in str(task.designer or "").split("\n")
        if _normalize_text(item)
    ]
    return target in values


def _task_stage_preview(task: _GroupTaskProjection, due_date: pd.Timestamp) -> str:
    stages = task.timing.get(due_date, [])
    if not stages:
        return "этап не указан"
    return ", ".join(str(stage) for stage in stages[:2])


def _sort_by_due_date(item: tuple[pd.Timestamp, _GroupTaskProjection]) -> pd.Timestamp:
    return item[0]


def _build_tasks_reply(tasks: list[_GroupTaskProjection], requester_name: str) -> str:
    now = pd.Timestamp.today().normalize()
    matched = [task for task in tasks if _task_matches_designer(task, requester_name)]
    if not matched:
        return f"@{requester_name}, не вижу активных задач на ваше имя."
    rows: list[tuple[pd.Timestamp, _GroupTaskProjection]] = []
    for task in matched:
        due_date = _task_due_date(task, now)
        if due_date is not None:
            rows.append((due_date, task))
    rows.sort(key=_sort_by_due_date)
    preview = rows[:7]
    lines = [f"@{requester_name}, ваши ближайшие задачи:"]
    for idx, (due_date, task) in enumerate(preview, start=1):
        lines.append(f"{idx}. {due_date.strftime('%d.%m')} - {task.name} ({_task_stage_preview(task, due_date)})")
    if len(rows) > len(preview):
        lines.append(f"... и еще {len(rows) - len(preview)} задач.")
    return "\n".join(lines)


def _build_deadlines_reply(tasks: list[_GroupTaskProjection]) -> str:
    now = pd.Timestamp.today().normalize()
    rows: list[tuple[pd.Timestamp, _GroupTaskProjection]] = []
    for task in tasks:
        due_date = _task_due_date(task, now)
        if due_date is not None:
            rows.append((due_date, task))
    if not rows:
        return "Ближайших дедлайнов не найдено."
    rows.sort(key=_sort_by_due_date)
    preview = rows[:10]
    lines = ["Ближайшие дедлайны по команде:"]
    for idx, (due_date, task) in enumerate(preview, start=1):
        lines.append(
            f"{idx}. {due_date.strftime('%d.%m')} - {task.name} [{task.designer}] ({_task_stage_preview(task, due_date)})"
        )
    if len(rows) > len(preview):
        lines.append(f"... и еще {len(rows) - len(preview)} задач.")
    return "\n".join(lines)


class GroupQueryHandler:
    """Telegram group query webhook handler."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None

        deps = self._ctx.deps
        bot_username = str(deps.get("tg_bot_username", ""))
        query = _parse_group_query_request(req.body, bot_username=bot_username)
        if query is None:
            return None

        notifier = TelegramNotifier(
            bot_token=str(deps.get("tg_bot_token", "")),
            default_chat_id=deps.get("default_chat_id"),
        )
        try:
            snapshot_engine = build_snapshot_engine(self._ctx)
            payload = snapshot_engine.frontend_v2(
                build_frontend_query(
                    statuses=["work", "pre_done"],
                    designer="",
                    limit=2000,
                    include_people=True,
                    window_data={"enabled": False, "start": None, "end": None, "mode": "intersects"},
                )
            )
            tasks = _group_tasks_from_payload(payload)
            if query.action == "deadlines":
                reply = _build_deadlines_reply(tasks)
            else:
                reply = _build_tasks_reply(tasks, requester_name=query.requester_name)
            await notifier.send_message(query.chat_id, reply, parse_mode=None)
            return json_response(200, {"artifact": "group_query", "status": "ok"})
        except Exception as error:
            print(f"group_query_error={error}")
            await notifier.send_message(
                query.chat_id,
                "Не удалось обработать запрос. Попробуйте позже или сообщите владельцу.",
                parse_mode=None,
            )
            return json_response(200, {"artifact": "group_query", "status": "error"})

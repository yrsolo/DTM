"""Group-query HTTP handler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.adapters.telegram import TelegramNotifier
from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.response_utils import json_response
from src.notify import GroupQueryFormatter, ReminderRequest, ReminderUseCase
from src.snapshot_engine import build_snapshot_engine

SUPPORTED_CHAT_TYPES = frozenset({"group", "supergroup"})
TASK_COMMANDS = ("/tasks", "/задачи")
DEADLINE_COMMANDS = ("/deadlines", "/дедлайны")


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
    return bool(username) and f"@{username}" in text.lower()


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


class GroupQueryHandler:
    """Telegram group query webhook handler."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None

        deps = self._ctx.deps
        query = _parse_group_query_request(req.body, bot_username=str(deps.get("tg_bot_username", "")))
        if query is None:
            return None

        notifier = TelegramNotifier(
            bot_token=str(deps.get("tg_bot_token", "")),
            default_chat_id=deps.get("default_chat_id"),
        )
        try:
            usecase = ReminderUseCase(build_snapshot_engine(self._ctx))
            groups, today, next_workday = usecase.select(
                ReminderRequest(
                    mode="group_query",
                    statuses=["work", "pre_done"],
                    include_today=True,
                    include_next_workday=True,
                )
            )
            formatter = GroupQueryFormatter()
            if query.action == "deadlines":
                reply = formatter.build_deadlines_reply(groups, today=today, next_workday=next_workday)
            else:
                reply = formatter.build_tasks_reply(
                    groups,
                    requester_name=query.requester_name,
                    today=today,
                    next_workday=next_workday,
                )
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

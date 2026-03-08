from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.commands.types import GROUP_QUERY_REPLY, SEND_REMINDERS, UPDATE_SNAPSHOT

SUPPORTED_CHAT_TYPES = frozenset({"private", "group", "supergroup"})
TASK_COMMANDS = ("/tasks", "/задачи")
DEADLINE_COMMANDS = ("/deadlines", "/дедлайны")
UPDATE_COMMANDS = ("/update", "/update_snapshot", "/refresh")
TEST_REMINDER_COMMANDS = ("/reminders_test", "/notify_test")


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_spaces(value: str) -> str:
    return " ".join(str(value or "").split())


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


@dataclass(frozen=True, slots=True)
class ParsedTelegramUpdate:
    chat_id: str
    chat_type: str
    user_id: str
    requester_name: str
    text: str


@dataclass(frozen=True, slots=True)
class ParsedTelegramAction:
    command_type: str
    payload: dict[str, Any]


class TelegramUpdateParser:
    def parse(self, update_json: dict[str, Any]) -> ParsedTelegramUpdate | None:
        message = update_json.get("message")
        if not isinstance(message, dict):
            return None
        chat = message.get("chat") or {}
        if str(chat.get("type", "")).strip() not in SUPPORTED_CHAT_TYPES:
            return None
        chat_id = _normalize_text(chat.get("id"))
        text = _normalize_text(message.get("text"))
        if not chat_id or not text:
            return None
        message_from = message.get("from") or {}
        return ParsedTelegramUpdate(
            chat_id=chat_id,
            chat_type=_normalize_text(chat.get("type")),
            user_id=_normalize_text(message_from.get("id")),
            requester_name=_requester_name(message_from),
            text=text,
        )

    def detect_action(
        self,
        parsed_update: ParsedTelegramUpdate,
        *,
        bot_username: str,
        default_chat_id: str = "",
    ) -> ParsedTelegramAction | None:
        text = parsed_update.text
        command = text.split(" ", 1)[0].strip()
        lowered = text.lower()
        username = _normalize_text(bot_username).lstrip("@").lower()
        base, _, suffix = command.partition("@")
        if suffix and username and suffix.lower() != username:
            return None

        if parsed_update.chat_type in {"group", "supergroup"}:
            action = None
            if base.lower() in TASK_COMMANDS:
                action = "tasks"
            elif base.lower() in DEADLINE_COMMANDS:
                action = "deadlines"
            elif username and f"@{username}" in lowered:
                action = "deadlines" if any(token in lowered for token in ("дедлайн", "срок", "deadline")) else "tasks"
            if action is None:
                return None
            return ParsedTelegramAction(
                command_type=GROUP_QUERY_REPLY,
                payload={
                    "chat_id": parsed_update.chat_id,
                    "requester_name": parsed_update.requester_name,
                    "action": action,
                    "statuses": ["work", "pre_done"],
                    "include_today": True,
                    "include_next_workday": True,
                },
            )

        if parsed_update.chat_type == "private" and parsed_update.chat_id == str(default_chat_id or "").strip():
            if base.lower() in UPDATE_COMMANDS:
                return ParsedTelegramAction(
                    command_type=UPDATE_SNAPSHOT,
                    payload={"force_refresh": True, "dry_run": False},
                )
            if base.lower() in TEST_REMINDER_COMMANDS:
                return ParsedTelegramAction(
                    command_type=SEND_REMINDERS,
                    payload={
                        "mode": "test",
                        "statuses": ["work", "pre_done"],
                        "include_today": True,
                        "include_next_workday": True,
                        "force_test_chat": True,
                        "mock_external": False,
                    },
                )
        return None

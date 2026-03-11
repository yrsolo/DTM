from __future__ import annotations

from typing import Any

from .model import ParsedTelegramUpdate

SUPPORTED_CHAT_TYPES = frozenset({"private", "group", "supergroup"})


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


class TelegramUpdateParser:
    """Thin Telegram update parser without business routing logic."""

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
        command = ""
        args = ""
        first_token = text.split(" ", 1)[0].strip()
        if first_token.startswith("/"):
            base, _, _suffix = first_token.partition("@")
            command = base.lower()
            args = text.split(" ", 1)[1].strip() if " " in text else ""
        return ParsedTelegramUpdate(
            update_type="message",
            chat_id=chat_id,
            chat_type=_normalize_text(chat.get("type")),
            user_id=_normalize_text(message_from.get("id")),
            requester_name=_requester_name(message_from),
            text=text,
            command=command,
            args=args,
            raw=dict(update_json),
        )

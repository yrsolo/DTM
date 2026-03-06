from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Iterable

from .formatter import FormattedMessage


class TelegramClient:
    def send_message(self, chat_id: str, text: str) -> Awaitable[object]:
        raise NotImplementedError


class TelegramReminderSender:
    def __init__(self, tg: TelegramClient, *, default_chat_id: str | int | None = None):
        self._tg = tg
        self._default_chat_id = None if default_chat_id is None else str(default_chat_id).strip()

    async def send(self, messages: Iterable[FormattedMessage]) -> None:
        for item in messages:
            target = str(item.chat_id or "").strip()
            if not target.lstrip("-").isdigit():
                target = str(self._default_chat_id or "").strip()
            if not target:
                continue
            await self._tg.send_message(target, item.text)

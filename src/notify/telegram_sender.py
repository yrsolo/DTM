from __future__ import annotations

from collections.abc import Iterable

from .formatter import FormattedMessage


class TelegramClient:
    def send_message(self, chat_id: str, text: str) -> None:
        raise NotImplementedError


class TelegramReminderSender:
    def __init__(self, tg: TelegramClient):
        self._tg = tg

    def send(self, messages: Iterable[FormattedMessage]) -> None:
        raise NotImplementedError

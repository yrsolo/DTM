from __future__ import annotations

from collections.abc import Awaitable
from typing import Protocol


class TelegramClient(Protocol):
    def send_message(self, chat_id: str, text: str) -> Awaitable[object]:
        raise NotImplementedError

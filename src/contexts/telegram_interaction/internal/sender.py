from __future__ import annotations

from src.platform.integrations.telegram.notifier import TelegramNotifier


class TelegramSender:
    def __init__(self, bot_token: str | None = None, default_chat_id: str | int | None = None) -> None:
        self._notifier = TelegramNotifier(bot_token=bot_token, default_chat_id=default_chat_id)

    async def send_message(self, chat_id: str | int, text: str, parse_mode: str | None = None):
        return await self._notifier.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

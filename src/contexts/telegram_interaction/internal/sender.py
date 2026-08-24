from __future__ import annotations


class TelegramSender:
    def __init__(self, sender_factory) -> None:  # noqa: ANN001
        self._sender_factory = sender_factory

    async def send_message(self, chat_id: str | int, text: str, parse_mode: str | None = None):
        async with self._sender_factory.session() as notifier:
            return await notifier.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

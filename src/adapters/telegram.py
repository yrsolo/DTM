"""Telegram adapter boundary."""

from __future__ import annotations

import asyncio
from typing import Any


def _safe_print(text: Any) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("unicode_escape").decode("ascii"))


class TelegramNotifier:
    """Thin adapter for Telegram bot message delivery."""

    def __init__(self, bot_token: str | None = None, default_chat_id: str | int | None = None) -> None:
        self._bot_token = bot_token
        self._bot = None
        self.default_chat_id = default_chat_id

    def _get_bot(self) -> Any:
        if not self._bot_token:
            raise RuntimeError("Telegram bot token is empty; pass bot_token explicitly.")
        if self._bot is None:
            try:
                from telegram.ext import Application
            except Exception as error:
                raise RuntimeError("Optional dep for Telegram adapter is missing: install `python-telegram-bot`.") from error
            self._bot = Application.builder().token(self._bot_token).build().bot
        return self._bot

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str | None = "Markdown",
    ) -> Any:
        try:
            bot = self._get_bot()
            return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        except Exception as error:
            _safe_print(f"Ошибка при отправке сообщения в Telegram: {error}")
            _safe_print("Повторная попытка отправки сообщения в Telegram без разметки")
            _safe_print(f"Лог в Telegram пропущен: {error}")
            try:
                bot = self._get_bot()
                return await bot.send_message(chat_id=chat_id, text=text, parse_mode=None)
            except Exception as error:
                _safe_print(f"Ошибка при отправке сообщения в Telegram без разметки: {error}")
                _safe_print(f"Сообщение: {text}")
        return None

    def log(self, text: str) -> None:
        if self.default_chat_id is None:
            raise RuntimeError("Default Telegram chat id is empty; pass default_chat_id explicitly.")
        func = self.send_message(self.default_chat_id, text)
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(func, loop)

    async def alog(self, text: str) -> Any:
        if self.default_chat_id is None:
            raise RuntimeError("Default Telegram chat id is empty; pass default_chat_id explicitly.")
        return await self.send_message(self.default_chat_id, text, parse_mode=None)

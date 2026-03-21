"""Domain person models."""

from __future__ import annotations

from typing import Any

from src.core.contracts import normalize_text


class Person:
    """Domain model for a project participant."""

    def __init__(
        self,
        person_id: Any,
        name: Any,
        email: Any,
        position: Any,
        telegram_id: Any,
        chat_id: Any,
        info: Any,
        vacation: Any,
        tg_bot: Any = None,
        **kwargs: Any,
    ) -> None:
        _ = kwargs
        self.id = normalize_text(person_id)
        self.name = normalize_text(name)
        self.email = normalize_text(email)
        self.telegram_id = normalize_text(telegram_id)
        self.chat_id = normalize_text(chat_id)
        self.tg_bot = tg_bot
        self.info = normalize_text(info, strip=False)
        self.position = normalize_text(position).lower()
        self.vacation = normalize_text(vacation).lower()
        self.tasks: list[Any] = []

    def __repr__(self) -> str:
        return self.name

    def send_message(self, message: str, to_chat: bool = True) -> None:
        if not self.tg_bot:
            return
        if to_chat:
            self.tg_bot.send_message(self.chat_id, message)
        else:
            self.tg_bot.send_message(self.telegram_id, message)


class Designer(Person):
    """Designer person specialization."""

    def __repr__(self) -> str:
        return f"Designer({self.name})"


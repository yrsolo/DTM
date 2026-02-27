"""Adapter boundary contracts for external integrations."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ChatAdapter(Protocol):
    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        ...


@runtime_checkable
class MessageAdapter(Protocol):
    async def send_message(self, chat_id: Any, text: str, parse_mode: str | None = "Markdown") -> Any:
        ...


@runtime_checkable
class LoggerAdapter(Protocol):
    def log(self, text: str) -> None:
        ...


class NullLogger:
    def log(self, text: str) -> None:
        return None

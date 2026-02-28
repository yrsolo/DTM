"""Adapter boundary contracts for external integrations."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ChatAdapter(Protocol):
    """Chat completion adapter contract."""

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        ...


@runtime_checkable
class MessageAdapter(Protocol):
    """Outbound message delivery adapter contract."""

    async def send_message(self, chat_id: Any, text: str, parse_mode: str | None = "Markdown") -> Any:
        ...


@runtime_checkable
class LoggerAdapter(Protocol):
    """Logging sink contract."""

    def log(self, text: str) -> None:
        ...


@runtime_checkable
class SheetRenderAdapter(Protocol):
    """Sheet rendering adapter contract used by manager layer."""

    def begin(self) -> None:
        ...

    def clear_cells(self, range_: str = "A1:ZZ1000") -> None:
        ...

    def clear_requests(self) -> None:
        ...

    def update_cell(self, cell_data: dict[str, Any]) -> None:
        ...

    def update_borders(self, border_data: dict[str, Any]) -> None:
        ...

    def execute_updates(self) -> None:
        ...


class NullLogger:
    """No-op logger implementation for optional logging dependency."""

    def log(self, text: str) -> None:
        _ = text
        return None

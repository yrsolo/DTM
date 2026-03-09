from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ParsedTelegramUpdate:
    update_type: str
    chat_id: str
    chat_type: str
    user_id: str
    requester_name: str
    text: str
    command: str = ""
    args: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RoutedTelegramCommand:
    command_name: str
    command_type: str
    payload: dict[str, Any]

from __future__ import annotations

from dataclasses import dataclass

from .model import ReminderResult


@dataclass(frozen=True)
class FormattedMessage:
    chat_id: str
    text: str


class ReminderFormatter:
    """Convert ReminderResult into formatted outgoing messages."""

    def format(self, result: ReminderResult) -> list[FormattedMessage]:
        raise NotImplementedError

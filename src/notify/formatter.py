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
        messages: list[FormattedMessage] = []
        for group in result.groups:
            header = f"Напоминания: {group.owner_id}"
            lines = [header]
            for task in group.tasks:
                title = str(task.sheet.title or "").strip() or str(task.sheet.task_id)
                status = str(task.sheet.status or "").strip() or "unknown"
                history = str(task.sheet.history or "").strip()
                if history:
                    lines.append(f"- {title} [{status}] — {history}")
                else:
                    lines.append(f"- {title} [{status}]")
            messages.append(
                FormattedMessage(
                    chat_id=str(group.owner_id),
                    text="\n".join(lines),
                )
            )
        return messages

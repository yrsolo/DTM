from __future__ import annotations

from .formatter import ReminderFormatter
from .model import ReminderRequest
from .telegram_sender import TelegramReminderSender
from .usecase import ReminderUseCase


class ReminderJob:
    """Orchestration boundary: query -> format -> send."""

    def __init__(self, usecase: ReminderUseCase, formatter: ReminderFormatter, sender: TelegramReminderSender):
        self._usecase = usecase
        self._formatter = formatter
        self._sender = sender

    def run(self, req: ReminderRequest) -> None:
        raise NotImplementedError

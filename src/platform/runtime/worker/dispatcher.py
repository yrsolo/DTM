from __future__ import annotations

from typing import Any

from src.platform.runtime.commands.model import Command
from src.platform.runtime.queue_dispatch import dispatch_command

from .model import JobResult


class CommandDispatcher:
    def __init__(self, command_handlers: dict[str, Any]) -> None:
        self._command_handlers = dict(command_handlers)

    async def dispatch(self, cmd: Command) -> JobResult:
        return await dispatch_command(cmd, command_handlers=self._command_handlers)


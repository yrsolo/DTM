from __future__ import annotations

import inspect
from typing import Any

from src.commands.model import Command
from src.commands.types import (
    GROUP_QUERY_REPLY,
    RENDER_DESIGNERS_SHEET,
    RENDER_TIMELINE_SHEET,
    SEND_REMINDERS,
    SUPPORTED_COMMAND_TYPES,
    UPDATE_SNAPSHOT,
)

from .model import JobResult


class CommandDispatcher:
    def __init__(
        self,
        update_snapshot_job: Any,
        send_reminders_job: Any,
        render_timeline_job: Any,
        render_designers_job: Any,
        group_query_reply_job: Any,
    ) -> None:
        self._handlers = {
            UPDATE_SNAPSHOT: update_snapshot_job,
            SEND_REMINDERS: send_reminders_job,
            RENDER_TIMELINE_SHEET: render_timeline_job,
            RENDER_DESIGNERS_SHEET: render_designers_job,
            GROUP_QUERY_REPLY: group_query_reply_job,
        }

    async def dispatch(self, cmd: Command) -> JobResult:
        if cmd.type not in SUPPORTED_COMMAND_TYPES:
            return JobResult(
                success=False,
                error={"code": "unsupported_command_type", "details": {"type": cmd.type}},
            )
        job = self._handlers[cmd.type]
        result = job.run(cmd)
        if inspect.isawaitable(result):
            result = await result
        details = dict(result or {}) if isinstance(result, dict) else {"result": result}
        status = str(details.get("status", "ok")).strip().lower()
        error = details.get("error")
        return JobResult(
            success=status not in {"failed", "blocked", "error"},
            details=details,
            warnings=[str(item) for item in list(details.get("warnings", []) or [])],
            error=dict(error or {}) if isinstance(error, dict) and error else None,
        )

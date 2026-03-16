from __future__ import annotations

import inspect
from typing import Any

from src.commands.model import Command
from src.commands.types import (
    ATTACH_TASK_FILE,
    CLEANUP_TASK_ATTACHMENTS,
    DELETE_TASK_ATTACHMENT,
    GENERATE_ATTACHMENT_PREVIEW,
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
        attach_task_file_job: Any,
        delete_task_attachment_job: Any,
        cleanup_task_attachments_job: Any,
        generate_attachment_preview_job: Any,
    ) -> None:
        self._handlers = {
            UPDATE_SNAPSHOT: update_snapshot_job,
            SEND_REMINDERS: send_reminders_job,
            RENDER_TIMELINE_SHEET: render_timeline_job,
            RENDER_DESIGNERS_SHEET: render_designers_job,
            GROUP_QUERY_REPLY: group_query_reply_job,
            ATTACH_TASK_FILE: attach_task_file_job,
            DELETE_TASK_ATTACHMENT: delete_task_attachment_job,
            CLEANUP_TASK_ATTACHMENTS: cleanup_task_attachments_job,
            GENERATE_ATTACHMENT_PREVIEW: generate_attachment_preview_job,
        }

    async def dispatch(self, cmd: Command) -> JobResult:
        if cmd.type not in SUPPORTED_COMMAND_TYPES:
            return JobResult(
                success=False,
                retryable=False,
                failure_kind="terminal",
                error_code="unsupported_command_type",
                error={"code": "unsupported_command_type", "details": {"type": cmd.type}},
            )
        job = self._handlers[cmd.type]
        result = job.run(cmd)
        if inspect.isawaitable(result):
            result = await result
        details = dict(result or {}) if isinstance(result, dict) else {"result": result}
        status = str(details.get("status", "ok")).strip().lower()
        error = details.get("error")
        retryable = bool(details.get("retryable", False))
        failure_kind = str(details.get("failure_kind", "")).strip().lower()
        error_code = str(details.get("error_code", "")).strip()
        if status in {"failed", "error"} and not failure_kind:
            failure_kind = "retryable" if retryable else "terminal"
        if status == "blocked" and not failure_kind:
            failure_kind = "terminal"
        if isinstance(error, dict) and error and not error_code:
            error_code = str(error.get("code", "")).strip()
        return JobResult(
            success=status not in {"failed", "blocked", "error"},
            retryable=retryable,
            failure_kind=failure_kind,
            error_code=error_code,
            details=details,
            warnings=[str(item) for item in list(details.get("warnings", []) or [])],
            error=dict(error or {}) if isinstance(error, dict) and error else None,
        )

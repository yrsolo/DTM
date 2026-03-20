"""Explicit queue dispatch for the target platform layer."""

from __future__ import annotations

import inspect
from typing import Any, Mapping

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
from src.worker.model import JobResult


async def dispatch_command(
    command: Command,
    *,
    command_handlers: Mapping[str, Any],
) -> JobResult:
    """Route a command explicitly by command type."""

    if command.type not in SUPPORTED_COMMAND_TYPES:
        return JobResult(
            success=False,
            retryable=False,
            failure_kind="terminal",
            error_code="unsupported_command_type",
            error={"code": "unsupported_command_type", "details": {"type": command.type}},
        )

    job = command_handlers.get(command.type)
    if job is None:
        return JobResult(
            success=False,
            retryable=False,
            failure_kind="terminal",
            error_code="unsupported_command_type",
            error={"code": "unsupported_command_type", "details": {"type": command.type}},
        )

    result = job.run(command)
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

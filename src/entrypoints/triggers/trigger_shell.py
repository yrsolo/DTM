"""Scheduled trigger shell for queue-backed or direct runtime execution."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.platform.context import AppContext
from src.platform.runtime.commands.model import Command, RequestedBy
from src.entrypoints.http.dto import to_gateway_response
from src.entrypoints.http.runtime_execution import RuntimeExecutionRequest
from src.platform.runtime.command_runtime import get_command_runtime
from src.entrypoints.runtime.runtime_shell import RuntimeShell
from src.entrypoints.triggers.trigger_plan import planned_trigger_commands


class TriggerShell:
    def __init__(self, ctx: AppContext, *, runtime_shell: RuntimeShell) -> None:
        self._ctx = ctx
        self._runtime_shell = runtime_shell

    def _enqueue_trigger_command(self, *, trigger_mode: str) -> dict[str, Any] | None:
        command_runtime = get_command_runtime(self._ctx)
        if not command_runtime.can_enqueue():
            return None
        mode = str(trigger_mode or "").strip().lower()
        planned = planned_trigger_commands(mode)
        if not planned:
            return None
        commands: list[dict[str, Any]] = []
        for command_type, payload in planned:
            cmd = Command(
                job_id=uuid4().hex,
                type=command_type,
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="trigger"),
                payload=dict(payload),
            )
            try:
                command_runtime.enqueue(cmd)
            except Exception as error:
                commands.append(
                    {
                        "command_type": cmd.type,
                        "status": "enqueue_failed",
                        "payload": dict(cmd.payload),
                        "error": {
                            "type": type(error).__name__,
                            "message": str(error),
                        },
                    }
                )
                continue
            commands.append(
                {
                    "job_id": cmd.job_id,
                    "command_type": cmd.type,
                    "status": "accepted",
                    "payload": dict(cmd.payload),
                }
            )
        accepted_commands = [item for item in commands if str(item.get("status", "")) == "accepted"]
        if not accepted_commands:
            return {
                "artifact": "command_batch_enqueue_failed" if len(commands) > 1 else "command_enqueue_failed",
                "status": "failed",
                "trigger_mode": mode,
                "queued_count": 0,
                "commands": commands,
                "error": {
                    "code": "trigger_enqueue_failed",
                    "message": "Failed to enqueue any planned trigger commands.",
                },
            }
        return {
            "artifact": "command_batch_enqueued" if len(commands) > 1 else "command_enqueued",
            "status": "accepted" if len(accepted_commands) == len(commands) else "partial_accept",
            "trigger_mode": mode,
            "queued_count": len(accepted_commands),
            "commands": commands,
            "job_id": accepted_commands[0]["job_id"],
            "command_type": accepted_commands[0]["command_type"],
        }

    async def handle_trigger(self, trigger_mode: str, event: Any) -> dict[str, Any]:
        enqueue_result = self._enqueue_trigger_command(trigger_mode=trigger_mode)
        if enqueue_result is not None:
            queued_count = int(enqueue_result.get("queued_count", 0) or 0)
            status_code = 200 if queued_count > 0 else 503
            return {"statusCode": status_code, "body": json.dumps(enqueue_result, ensure_ascii=False)}
        runtime_response = await self._runtime_shell.execute(
            RuntimeExecutionRequest(
                mode=str(trigger_mode or "").strip().lower(),
                planner_event=event,
                dry_run=False,
                mock_external=None,
                force_refresh=False,
            ),
            is_http_event=False,
        )
        return to_gateway_response(runtime_response)


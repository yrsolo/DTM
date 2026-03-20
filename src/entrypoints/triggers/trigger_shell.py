"""Scheduled trigger shell for queue-backed or direct runtime execution."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
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
            command_runtime.enqueue(cmd)
            commands.append(
                {
                    "job_id": cmd.job_id,
                    "command_type": cmd.type,
                    "payload": dict(cmd.payload),
                }
            )
        return {
            "artifact": "command_batch_enqueued" if len(commands) > 1 else "command_enqueued",
            "status": "accepted",
            "trigger_mode": mode,
            "queued_count": len(commands),
            "commands": commands,
            "job_id": commands[0]["job_id"],
            "command_type": commands[0]["command_type"],
        }

    async def handle_trigger(self, trigger_mode: str, event: Any) -> dict[str, Any]:
        enqueue_result = self._enqueue_trigger_command(trigger_mode=trigger_mode)
        if enqueue_result is not None:
            return {"statusCode": 200, "body": json.dumps(enqueue_result, ensure_ascii=False)}
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

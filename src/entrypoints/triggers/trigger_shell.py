"""Scheduled trigger shell for queue-backed or direct runtime execution."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.commands.types import SEND_REMINDERS, UPDATE_SNAPSHOT
from src.entrypoints.http.dto import to_gateway_response
from src.entrypoints.http.runtime_execution import RuntimeExecutionRequest
from src.entrypoints.runtime.runtime_shell import RuntimeShell


class TriggerShell:
    def __init__(self, ctx: AppContext, *, runtime_shell: RuntimeShell) -> None:
        self._ctx = ctx
        self._runtime_shell = runtime_shell

    def _enqueue_trigger_command(self, *, trigger_mode: str) -> dict[str, Any] | None:
        producer = self._ctx.deps.get("command_queue_producer")
        status_store = self._ctx.deps.get("job_status_store")
        if producer is None or status_store is None:
            return None
        mode = str(trigger_mode or "").strip().lower()
        if mode == "timer":
            command_type = UPDATE_SNAPSHOT
            payload: dict[str, Any] = {"force_refresh": False, "dry_run": False}
        elif mode == "morning":
            command_type = SEND_REMINDERS
            payload = {
                "mode": "morning",
                "statuses": ["work", "pre_done"],
                "include_today": True,
                "include_next_workday": True,
                "force_test_chat": False,
                "mock_external": False,
            }
        else:
            return None
        cmd = Command(
            job_id=uuid4().hex,
            type=command_type,
            created_at_utc=datetime.now(timezone.utc),
            requested_by=RequestedBy(source="trigger"),
            payload=payload,
        )
        producer.send(cmd)
        status_store.put_queued(cmd)
        return {
            "artifact": "command_enqueued",
            "status": "accepted",
            "job_id": cmd.job_id,
            "command_type": cmd.type,
            "trigger_mode": mode,
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

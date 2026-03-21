"""Queue-trigger shell for command worker execution."""

from __future__ import annotations

import json
from typing import Any

from src.platform.context import AppContext
from src.platform.runtime.commands.yandex_mq import queue_messages_from_event
from src.platform.runtime.command_runtime import get_command_runtime


class WorkerShell:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def handle_queue_event(self, event: Any) -> dict[str, Any]:
        worker = get_command_runtime(self._ctx).get_worker()
        if worker is None:
            return {
                "statusCode": 503,
                "body": json.dumps(
                    {
                        "artifact": "command_worker",
                        "status": "queue_unavailable",
                    },
                    ensure_ascii=False,
                ),
            }
        result = await worker.run_once_from_messages(queue_messages_from_event(event))
        retry_requested = bool(result.get("retry_requested", False))
        status_code = 503 if retry_requested else 200
        return {"statusCode": status_code, "body": json.dumps(result, ensure_ascii=False)}


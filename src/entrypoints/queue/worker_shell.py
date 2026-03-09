"""Queue-trigger shell for command worker execution."""

from __future__ import annotations

import json
from typing import Any

from src.app.context import AppContext
from src.commands.yandex_mq import queue_messages_from_event


class WorkerShell:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def handle_queue_event(self, event: Any) -> dict[str, Any]:
        worker = self._ctx.deps.get("command_worker")
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
        return {"statusCode": 200, "body": json.dumps(result, ensure_ascii=False)}

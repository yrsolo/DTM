"""Top-level dispatcher for Cloud Function entrypoint events."""

from __future__ import annotations

from typing import Any

from src.app.context import AppContext
from src.entrypoints.event_classifier import EventKind, classify_event
from src.entrypoints.http.http_shell import HttpShell
from src.entrypoints.queue.worker_shell import WorkerShell
from src.entrypoints.runtime.runtime_shell import RuntimeShell
from src.entrypoints.triggers.trigger_shell import TriggerShell


class IndexDispatcher:
    def __init__(self, ctx: AppContext, *, triggers: dict[str, str] | None = None) -> None:
        self._ctx = ctx
        self._triggers = triggers if triggers is not None else dict(ctx.cfg.runtime.triggers)
        runtime_shell = RuntimeShell(ctx)
        self._http_shell = HttpShell(ctx, runtime_shell=runtime_shell)
        self._worker_shell = WorkerShell(ctx)
        self._trigger_shell = TriggerShell(ctx, runtime_shell=runtime_shell)

    async def handle(self, event: Any, _yc_context: Any) -> dict[str, Any]:
        classification = classify_event(event, self._triggers)
        if classification.kind is EventKind.QUEUE:
            return await self._worker_shell.handle_queue_event(event)
        if classification.kind is EventKind.HEALTHCHECK:
            return {
                "statusCode": 200,
                "body": "!HEALTHY!",
            }
        if classification.kind is EventKind.HTTP:
            event_dict = event if isinstance(event, dict) else {}
            return await self._http_shell.handle(
                event_dict,
                classification.request_payload,
                classification.is_http_event,
            )
        if classification.kind is EventKind.TRIGGER:
            return await self._trigger_shell.handle_trigger(classification.trigger_mode, event)
        return {
            "statusCode": 200,
            "body": "!NOOP!",
        }

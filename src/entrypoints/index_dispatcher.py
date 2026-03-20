"""Compatibility dispatcher delegating to the thin target entrypoint."""

from __future__ import annotations

from typing import Any

from src.app.context import AppContext
from src.entrypoint.handler import handle as handle_entrypoint
from src.entrypoints.http.http_shell import HttpShell
from src.entrypoints.queue.worker_shell import WorkerShell
from src.entrypoints.runtime.runtime_shell import RuntimeShell
from src.entrypoints.triggers.trigger_shell import TriggerShell


class IndexDispatcher:
    """Transitional compatibility wrapper over the thin target entrypoint."""

    def __init__(self, ctx: AppContext, *, triggers: dict[str, str] | None = None) -> None:
        self._ctx = ctx
        self._triggers = triggers if triggers is not None else dict(ctx.cfg.runtime.triggers)
        runtime_shell = RuntimeShell(ctx)
        self._http_shell = HttpShell(ctx, runtime_shell=runtime_shell)
        self._worker_shell = WorkerShell(ctx)
        self._trigger_shell = TriggerShell(ctx, runtime_shell=runtime_shell)

    async def handle(self, event: Any, yc_context: Any) -> dict[str, Any]:
        return await handle_entrypoint(
            event,
            yc_context,
            get_http_shell=lambda: self._http_shell,
            get_worker_shell=lambda: self._worker_shell,
            get_trigger_shell=lambda: self._trigger_shell,
            triggers=self._triggers,
            telegram_webhook_path=self._ctx.cfg.runtime.telegram.webhook_path,
        )

"""Thin runtime shell bridging transport shells to shared runtime entry."""

from __future__ import annotations

from typing import Any

from src.app.context import AppContext
from src.entrypoints.http.runtime_execution import RuntimeExecutionRequest, RuntimeExecutor
from src.entrypoints.runtime.planner_runtime_entry import PlannerRuntimeRequest, run_planner_runtime


class RuntimeShell:
    def __init__(self, ctx: AppContext) -> None:
        self._executor = RuntimeExecutor(ctx)

    async def execute(self, request: RuntimeExecutionRequest, *, is_http_event: bool):
        return await self._executor.execute(
            request,
            main_func=run_planner_runtime,
            request_factory=PlannerRuntimeRequest,
            is_http_event=is_http_event,
        )

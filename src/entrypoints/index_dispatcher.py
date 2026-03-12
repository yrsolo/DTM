"""Top-level dispatcher for Cloud Function entrypoint events."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from src.app.context import AppContext
from src.entrypoints.event_classifier import EventKind, classify_event
from src.entrypoints.http.http_shell import HttpShell
from src.entrypoints.queue.worker_shell import WorkerShell
from src.entrypoints.runtime.runtime_shell import RuntimeShell
from src.entrypoints.triggers.trigger_shell import TriggerShell
from src.observability.bottlenecks import append_response_headers, is_stage_metrics_enabled, record_api_outer_stage


class IndexDispatcher:
    def __init__(self, ctx: AppContext, *, triggers: dict[str, str] | None = None) -> None:
        self._ctx = ctx
        self._triggers = triggers if triggers is not None else dict(ctx.cfg.runtime.triggers)
        runtime_shell = RuntimeShell(ctx)
        self._http_shell = HttpShell(ctx, runtime_shell=runtime_shell)
        self._worker_shell = WorkerShell(ctx)
        self._trigger_shell = TriggerShell(ctx, runtime_shell=runtime_shell)

    async def handle(self, event: Any, _yc_context: Any) -> dict[str, Any]:
        started_at = perf_counter()
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
            response = await self._http_shell.handle(
                event_dict,
                classification.request_payload,
                classification.is_http_event,
            )
            headers = dict(response.get("headers", {}) or {})
            trace_id = str(headers.get("X-DTM-Trace-Id", "")).strip() or str(headers.get("X-DTM-Outer-Trace-Id", "")).strip()
            if trace_id and is_stage_metrics_enabled(self._ctx):
                function_total_ms = (perf_counter() - started_at) * 1000.0
                record_api_outer_stage(
                    self._ctx,
                    trace_id=trace_id,
                    operation="/api/v2/frontend",
                    stage="function_total",
                    duration_ms=function_total_ms,
                )
                server_timing = str(headers.get("Server-Timing", "")).strip()
                server_timing = (
                    f"{server_timing}, function_total;dur={round(function_total_ms, 3)}"
                    if server_timing
                    else f"function_total;dur={round(function_total_ms, 3)}"
                )
                headers = append_response_headers(
                    headers,
                    {"Server-Timing": server_timing},
                )
                if str(self._ctx.cfg.runtime.runtime.bottleneck_metrics_level or "").strip().lower() == "debug":
                    headers = append_response_headers(
                        headers,
                        {"X-DTM-Outer-Function-Total-Ms": f"{function_total_ms:.3f}"},
                    )
                response["headers"] = headers
            return response
        if classification.kind is EventKind.TRIGGER:
            return await self._trigger_shell.handle_trigger(classification.trigger_mode, event)
        return {
            "statusCode": 200,
            "body": "!NOOP!",
        }

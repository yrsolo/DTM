from __future__ import annotations

from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Iterator
from uuid import uuid4


_ALLOWED_LEVELS = {"off", "stages", "debug"}


def _env_name(ctx: Any) -> str:
    try:
        return str(ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev"
    except Exception:
        return "dev"


def resolve_bottleneck_metrics_level(ctx: Any) -> str:
    try:
        level = str(ctx.cfg.runtime.runtime.bottleneck_metrics_level or "").strip().lower()
    except Exception:
        level = ""
    if level in _ALLOWED_LEVELS:
        return level
    try:
        if bool(ctx.cfg.runtime.runtime.dev_mode_metrics):
            return "stages"
    except Exception:
        pass
    return "off"


def is_stage_metrics_enabled(ctx: Any) -> bool:
    return resolve_bottleneck_metrics_level(ctx) in {"stages", "debug"}


def is_debug_metrics_enabled(ctx: Any) -> bool:
    return resolve_bottleneck_metrics_level(ctx) == "debug"


def is_detailed_metrics_enabled(ctx: Any) -> bool:
    return is_stage_metrics_enabled(ctx)


@dataclass(slots=True)
class StageEvent:
    trace_id: str
    recorded_at: str
    env: str
    operation: str
    stage: str
    duration_ms: float
    result: str
    route: str
    access_mode: str
    cache_result: str
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OuterApiTrace:
    trace_id: str
    recorded_at: str
    env: str
    operation: str
    result: str
    function_total_ms: float
    router_precheck_total_ms: float
    router_handler_total_ms: float
    router_total_ms: float
    http_shell_post_router_ms: float
    response_build_ms: float
    frontend_handler_total_ms: float
    frontend_inner_core_ms: float
    unexplained_inside_handler_ms: float
    unexplained_after_handler_ms: float
    debug: dict[str, Any] = field(default_factory=dict)


class RecentStageRecorder:
    def __init__(self, max_events: int = 200) -> None:
        self._events: deque[StageEvent] = deque(maxlen=max_events)

    def record(self, event: StageEvent) -> None:
        self._events.append(event)

    def recent_traces(self, limit: int = 10) -> list[dict[str, Any]]:
        traces: list[dict[str, Any]] = []
        trace_index: dict[str, dict[str, Any]] = {}
        for event in reversed(list(self._events)):
            trace = trace_index.get(event.trace_id)
            if trace is None:
                if len(traces) >= limit:
                    continue
                trace = {
                    "traceId": event.trace_id,
                    "recordedAt": event.recorded_at,
                    "env": event.env,
                    "operation": event.operation,
                    "route": event.route,
                    "accessMode": event.access_mode,
                    "cacheResult": event.cache_result,
                    "result": event.result,
                    "totalTrackedMs": 0.0,
                    "stages": [],
                    "debug": dict(event.debug or {}),
                }
                traces.append(trace)
                trace_index[event.trace_id] = trace
            trace["stages"].insert(
                0,
                {
                    "stage": event.stage,
                    "durationMs": round(float(event.duration_ms), 3),
                },
            )
            if not str(event.stage or "").strip().endswith("_total"):
                trace["totalTrackedMs"] = round(float(trace["totalTrackedMs"]) + float(event.duration_ms), 3)
            if event.debug and not trace["debug"]:
                trace["debug"] = dict(event.debug)
        return traces


RECENT_API_STAGE_EVENTS = RecentStageRecorder()


class RecentOuterTraceRecorder:
    def __init__(self, max_events: int = 50) -> None:
        self._events: deque[OuterApiTrace] = deque(maxlen=max_events)

    def record(self, trace: OuterApiTrace) -> None:
        self._events.append(trace)

    def recent_traces(self, limit: int = 10) -> list[dict[str, Any]]:
        traces: list[dict[str, Any]] = []
        for item in reversed(list(self._events)):
            if len(traces) >= limit:
                break
            traces.append(
                {
                    "traceId": item.trace_id,
                    "recordedAt": item.recorded_at,
                    "env": item.env,
                    "operation": item.operation,
                    "result": item.result,
                    "functionTotalMs": round(float(item.function_total_ms), 3),
                    "routerPrecheckTotalMs": round(float(item.router_precheck_total_ms), 3),
                    "routerHandlerTotalMs": round(float(item.router_handler_total_ms), 3),
                    "routerTotalMs": round(float(item.router_total_ms), 3),
                    "httpShellPostRouterMs": round(float(item.http_shell_post_router_ms), 3),
                    "responseBuildMs": round(float(item.response_build_ms), 3),
                    "frontendHandlerTotalMs": round(float(item.frontend_handler_total_ms), 3),
                    "frontendInnerCoreMs": round(float(item.frontend_inner_core_ms), 3),
                    "unexplainedInsideHandlerMs": round(float(item.unexplained_inside_handler_ms), 3),
                    "unexplainedAfterHandlerMs": round(float(item.unexplained_after_handler_ms), 3),
                    "debug": dict(item.debug or {}),
                }
            )
        return traces


RECENT_DIRECT_API_OUTER_TRACES = RecentOuterTraceRecorder()


def new_stage_trace_id() -> str:
    return uuid4().hex[:12]


def is_direct_api_operation(operation: str) -> bool:
    normalized = str(operation or "").strip().lower()
    return normalized.startswith("/api/") and not normalized.startswith("/bff/")


def record_api_stage(
    ctx: Any,
    *,
    trace_id: str,
    operation: str,
    stage: str,
    duration_ms: float,
    result: str = "success",
    route: str = "",
    access_mode: str = "",
    cache_result: str = "",
    debug_fields: dict[str, Any] | None = None,
) -> None:
    if not is_stage_metrics_enabled(ctx):
        return
    env_name = _env_name(ctx)
    labels = {
        "env": env_name,
        "module": "api",
        "operation": str(operation or "").strip() or "unknown",
        "stage": str(stage or "").strip() or "unknown",
        "result": str(result or "").strip() or "success",
    }
    if route:
        labels["route"] = str(route)
    if access_mode:
        labels["access_mode"] = str(access_mode)
    if cache_result:
        labels["cache_result"] = str(cache_result)
    metrics = None
    logger = None
    try:
        metrics = ctx.deps.get("metrics_client")
        logger = ctx.deps.get("structured_logger")
    except Exception:
        metrics = None
        logger = None
    if metrics is not None:
        metrics.timing("dtm.api.stage.duration_ms", float(duration_ms), labels=dict(labels))
        metrics.counter("dtm.api.stage.total", labels=dict(labels))
        if result != "success":
            metrics.counter("dtm.api.stage.failures_total", labels=dict(labels))
    debug_payload = dict(debug_fields or {}) if is_debug_metrics_enabled(ctx) else {}
    event = StageEvent(
        trace_id=str(trace_id or "").strip() or new_stage_trace_id(),
        recorded_at=datetime.now(timezone.utc).isoformat(),
        env=env_name,
        operation=str(operation or "").strip() or "unknown",
        stage=str(stage or "").strip() or "unknown",
        duration_ms=float(duration_ms),
        result=str(result or "").strip() or "success",
        route=str(route or "").strip(),
        access_mode=str(access_mode or "").strip(),
        cache_result=str(cache_result or "").strip(),
        debug=debug_payload,
    )
    RECENT_API_STAGE_EVENTS.record(event)
    if logger is not None and debug_payload:
        logger.info(
            "api_stage_timing",
            trace_id=event.trace_id,
            operation=event.operation,
            stage=event.stage,
            duration_ms=round(event.duration_ms, 3),
            route=event.route,
            access_mode=event.access_mode,
            cache_result=event.cache_result,
            result=event.result,
            debug=debug_payload,
        )


def record_api_outer_stage(
    ctx: Any,
    *,
    trace_id: str,
    operation: str,
    stage: str,
    duration_ms: float,
    result: str = "success",
    debug_fields: dict[str, Any] | None = None,
) -> None:
    if not is_stage_metrics_enabled(ctx):
        return
    labels = {
        "env": _env_name(ctx),
        "module": "api",
        "operation": str(operation or "").strip() or "unknown",
        "stage": str(stage or "").strip() or "unknown",
        "result": str(result or "").strip() or "success",
    }
    metrics = None
    logger = None
    try:
        metrics = ctx.deps.get("metrics_client")
        logger = ctx.deps.get("structured_logger")
    except Exception:
        metrics = None
        logger = None
    if metrics is not None:
        metrics.timing("dtm.api.outer.duration_ms", float(duration_ms), labels=dict(labels))
        metrics.counter("dtm.api.outer.total", labels=dict(labels))
        if result != "success":
            metrics.counter("dtm.api.outer.failures_total", labels=dict(labels))
    if logger is not None and is_debug_metrics_enabled(ctx):
        logger.info(
            "api_outer_timing",
            trace_id=str(trace_id or "").strip(),
            operation=str(operation or "").strip(),
            stage=str(stage or "").strip(),
            duration_ms=round(float(duration_ms), 3),
            result=str(result or "").strip() or "success",
            debug=dict(debug_fields or {}),
        )


def record_direct_api_outer_trace(
    ctx: Any,
    *,
    trace_id: str,
    operation: str,
    result: str,
    function_total_ms: float,
    router_precheck_total_ms: float,
    router_handler_total_ms: float,
    router_total_ms: float,
    http_shell_post_router_ms: float,
    response_build_ms: float,
    frontend_handler_total_ms: float,
    frontend_inner_core_ms: float,
    debug_fields: dict[str, Any] | None = None,
) -> None:
    if not is_stage_metrics_enabled(ctx):
        return
    env_name = _env_name(ctx)
    unexplained_inside_handler_ms = max(float(frontend_handler_total_ms) - float(frontend_inner_core_ms), 0.0)
    unexplained_after_handler_ms = max(float(function_total_ms) - float(frontend_handler_total_ms), 0.0)
    RECENT_DIRECT_API_OUTER_TRACES.record(
        OuterApiTrace(
            trace_id=str(trace_id or "").strip() or new_stage_trace_id(),
            recorded_at=datetime.now(timezone.utc).isoformat(),
            env=env_name,
            operation=str(operation or "").strip() or "unknown",
            result=str(result or "").strip() or "success",
            function_total_ms=float(function_total_ms),
            router_precheck_total_ms=float(router_precheck_total_ms),
            router_handler_total_ms=float(router_handler_total_ms),
            router_total_ms=float(router_total_ms),
            http_shell_post_router_ms=float(http_shell_post_router_ms),
            response_build_ms=float(response_build_ms),
            frontend_handler_total_ms=float(frontend_handler_total_ms),
            frontend_inner_core_ms=float(frontend_inner_core_ms),
            unexplained_inside_handler_ms=float(unexplained_inside_handler_ms),
            unexplained_after_handler_ms=float(unexplained_after_handler_ms),
            debug=dict(debug_fields or {}) if is_debug_metrics_enabled(ctx) else {},
        )
    )


def build_server_timing_header(timings: dict[str, float]) -> str:
    parts: list[str] = []
    for key, value in timings.items():
        parts.append(f"{str(key).strip()};dur={round(float(value), 3)}")
    return ", ".join(parts)


def append_response_headers(headers: dict[str, str] | None, extra: dict[str, str]) -> dict[str, str]:
    merged = dict(headers or {})
    for key, value in extra.items():
        text = str(value or "").strip()
        if text:
            merged[str(key)] = text
    return merged


@contextmanager
def api_stage_timer(
    ctx: Any,
    *,
    trace_id: str,
    operation: str,
    stage: str,
    route: str = "",
    access_mode: str = "",
    cache_result: str = "",
    debug_fields: dict[str, Any] | None = None,
) -> Iterator[None]:
    started = perf_counter()
    result = "success"
    try:
        yield
    except Exception:
        result = "failed"
        raise
    finally:
        record_api_stage(
            ctx,
            trace_id=trace_id,
            operation=operation,
            stage=stage,
            duration_ms=(perf_counter() - started) * 1000.0,
            result=result,
            route=route,
            access_mode=access_mode,
            cache_result=cache_result,
            debug_fields=debug_fields,
        )

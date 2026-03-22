"""Observability helper for the primary browser task-list read."""

from __future__ import annotations

import time

from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.platform.observability.bottlenecks import (
    append_response_headers,
    is_stage_metrics_enabled,
    new_stage_trace_id,
    record_api_stage,
)


class FrontendAccessObserver:
    """Own trace/stage bookkeeping for the primary browser read flow."""

    def __init__(self, ctx, req: HttpRequest) -> None:  # noqa: ANN001
        self._ctx = ctx
        self._req = req
        self._started = time.perf_counter()
        self._trace_id = new_stage_trace_id()
        self._stage_samples: list[tuple[str, float]] = []

    @property
    def trace_id(self) -> str:
        return self._trace_id

    def stage(self, stage: str, started_at: float) -> None:
        self._stage_samples.append((stage, (time.perf_counter() - started_at) * 1000.0))

    def add_sample(self, stage: str, duration_ms: float) -> None:
        self._stage_samples.append((stage, duration_ms))

    def inner_total_ms(self) -> float:
        return float(sum(duration_ms for _, duration_ms in self._stage_samples))

    def emit(
        self,
        *,
        route_class: str,
        access_mode: str,
        cache_result: str,
        result: str = "success",
        debug_fields: dict[str, object] | None = None,
    ) -> float:
        for stage, duration_ms in self._stage_samples:
            record_api_stage(
                self._ctx,
                trace_id=self._trace_id,
                operation="frontend_access",
                stage=stage,
                duration_ms=duration_ms,
                result=result,
                route=route_class,
                access_mode=access_mode,
                cache_result=cache_result,
                debug_fields=debug_fields,
            )
        handler_total_ms = (time.perf_counter() - self._started) * 1000.0
        record_api_stage(
            self._ctx,
            trace_id=self._trace_id,
            operation="frontend_access",
            stage="handler_total",
            duration_ms=handler_total_ms,
            result=result,
            route=route_class,
            access_mode=access_mode,
            cache_result=cache_result,
            debug_fields=debug_fields,
        )
        return handler_total_ms

    def debug_headers(
        self,
        *,
        req: HttpRequest,
        route_class: str,
        access_mode: str,
        cache_result: str,
        handler_total_ms: float,
    ) -> dict[str, str]:
        if not is_stage_metrics_enabled(self._ctx):
            return {}
        if req.path != "/api/v2/frontend":
            return {}
        if route_class != "api":
            return {}
        return {
            "X-DTM-Trace-Id": self._trace_id,
            "X-DTM-Frontend-Handler-Ms": f"{round(float(handler_total_ms), 3):.3f}",
            "X-DTM-Frontend-Inner-Ms": f"{round(self.inner_total_ms(), 3):.3f}",
            "X-DTM-Frontend-Route": route_class,
            "X-DTM-Frontend-Access-Mode": access_mode,
            "X-DTM-Frontend-Cache-Result": cache_result,
        }

    @staticmethod
    def with_headers(response: HttpResponse, extra_headers: dict[str, str]) -> HttpResponse:
        return HttpResponse(
            status=response.status,
            body=response.body,
            headers=append_response_headers(response.headers, extra_headers),
        )

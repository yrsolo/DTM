"""HTTP shell for request parsing, routing, and explicit runtime fallback."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from src.platform.context import AppContext
from src.entrypoints.http.debug_utils import debug_http_shape
from src.entrypoints.http.dto import HttpRequest, to_gateway_response
from src.entrypoints.http.event_parser import (
    header_params,
    http_method,
    http_path,
    normalize_path,
    query_params,
)
from src.entrypoints.http.response_utils import error_response, json_response
from src.entrypoints.http.router import HttpRouter
from src.entrypoints.http.runtime_execution import RuntimeExecutionRequest
from src.entrypoints.http.runtime_mode import extract_force_refresh, extract_run_mode
from src.entrypoints.http.frontend_query_params import parse_bool
from src.platform.observability.bottlenecks import (
    append_response_headers,
    build_server_timing_header,
    is_direct_api_operation,
    is_api_metrics_enabled,
    is_debug_metrics_enabled,
    is_stage_metrics_enabled,
    new_stage_trace_id,
    record_api_outer_stage,
    record_direct_api_outer_trace,
)
from src.platform.observability.buffered_metrics import managed_metrics_scope
from src.entrypoints.runtime.runtime_contract import STANDARD_RUN_MODES, is_legacy_mode
from src.entrypoints.runtime.runtime_shell import RuntimeShell


class HttpShell:
    def __init__(self, ctx: AppContext, *, runtime_shell: RuntimeShell) -> None:
        self._ctx = ctx
        self._runtime_shell = runtime_shell
        self._router = HttpRouter(ctx)
        self._debug_http_event = bool(ctx.cfg.runtime.api.get("debug_http_event_default", False))

    @staticmethod
    def _requested_mode(event: dict[str, Any], request_payload: dict[str, Any], is_http_event: bool) -> str:
        raw_mode = str(request_payload.get("mode", "")).strip().lower()
        if not raw_mode and is_http_event:
            raw_mode = str(query_params(event).get("mode", "")).strip().lower()
        return raw_mode

    @staticmethod
    def _header_float(headers: dict[str, str], key: str) -> float:
        try:
            return float(str(headers.get(key, "")).strip())
        except Exception:
            return 0.0

    @staticmethod
    def _pop_response_headers(headers: dict[str, str], *keys: str) -> dict[str, str]:
        cleaned = dict(headers or {})
        for key in keys:
            cleaned.pop(key, None)
        return cleaned

    def _finalize_direct_api_outer_response(
        self,
        *,
        response: dict[str, Any],
        operation: str,
        trace_id: str,
        started_at: float,
    ) -> dict[str, Any]:
        if not trace_id or not self._should_trace_direct_frontend(operation):
            return response
        headers = dict(response.get("headers", {}) or {})
        function_total_ms = (perf_counter() - started_at) * 1000.0
        record_api_outer_stage(
            self._ctx,
            trace_id=trace_id,
            operation=operation,
            stage="function_total",
            duration_ms=function_total_ms,
        )
        router_precheck_total_ms = self._header_float(headers, "X-DTM-Outer-Router-Precheck-Ms")
        router_handler_total_ms = self._header_float(headers, "X-DTM-Outer-Router-Handler-Ms")
        router_total_ms = self._header_float(headers, "X-DTM-Outer-Router-Total-Ms")
        http_shell_post_router_ms = self._header_float(headers, "X-DTM-Outer-Http-Shell-Post-Router-Ms")
        response_build_ms = self._header_float(headers, "X-DTM-Outer-Response-Build-Ms")
        frontend_handler_total_ms = self._header_float(headers, "X-DTM-Outer-Frontend-Handler-Ms")
        frontend_inner_core_ms = self._header_float(headers, "X-DTM-Outer-Frontend-Inner-Ms")
        access_mode = str(headers.get("X-DTM-Outer-Access-Mode", "")).strip()
        cache_result = str(headers.get("X-DTM-Outer-Cache-Result", "")).strip()
        route = str(headers.get("X-DTM-Outer-Route", "")).strip()
        router_handler_name = str(headers.get("X-DTM-Outer-Router-Handler-Name", "")).strip()
        request_build_ms = self._header_float(headers, "X-DTM-Outer-Request-Build-Ms")
        unexplained_after_handler_ms = max(function_total_ms - frontend_handler_total_ms, 0.0)
        unexplained_inside_handler_ms = max(frontend_handler_total_ms - frontend_inner_core_ms, 0.0)
        server_timing = str(headers.get("Server-Timing", "")).strip()
        server_timing = (
            f"{server_timing}, function_total;dur={round(function_total_ms, 3)}, unexplained_inside_handler;dur={round(unexplained_inside_handler_ms, 3)}, unexplained_after_handler;dur={round(unexplained_after_handler_ms, 3)}"
            if server_timing
            else f"function_total;dur={round(function_total_ms, 3)}, unexplained_inside_handler;dur={round(unexplained_inside_handler_ms, 3)}, unexplained_after_handler;dur={round(unexplained_after_handler_ms, 3)}"
        )
        headers = append_response_headers(headers, {"Server-Timing": server_timing})
        record_direct_api_outer_trace(
            self._ctx,
            trace_id=trace_id,
            operation=operation,
            result="success",
            function_total_ms=function_total_ms,
            router_precheck_total_ms=router_precheck_total_ms,
            router_handler_total_ms=router_handler_total_ms,
            router_total_ms=router_total_ms,
            http_shell_post_router_ms=http_shell_post_router_ms,
            response_build_ms=response_build_ms,
            frontend_handler_total_ms=frontend_handler_total_ms,
            frontend_inner_core_ms=frontend_inner_core_ms,
            debug_fields={
                "route": route,
                "accessMode": access_mode,
                "cacheResult": cache_result,
                "routerHandler": router_handler_name,
                "requestBuildMs": round(request_build_ms, 3),
            },
        )
        for internal_key in (
            "X-DTM-Outer-Router-Precheck-Ms",
            "X-DTM-Outer-Router-Handler-Ms",
            "X-DTM-Outer-Router-Total-Ms",
            "X-DTM-Outer-Http-Shell-Post-Router-Ms",
            "X-DTM-Outer-Response-Build-Ms",
            "X-DTM-Outer-Frontend-Handler-Ms",
            "X-DTM-Outer-Frontend-Inner-Ms",
            "X-DTM-Outer-Access-Mode",
            "X-DTM-Outer-Cache-Result",
            "X-DTM-Outer-Route",
            "X-DTM-Outer-Router-Handler-Name",
            "X-DTM-Outer-Request-Build-Ms",
        ):
            headers.pop(internal_key, None)
        if is_debug_metrics_enabled(self._ctx):
            headers = append_response_headers(
                headers,
                {
                    "X-DTM-Outer-Function-Total-Ms": f"{function_total_ms:.3f}",
                    "X-DTM-Outer-Unexplained-Inside-Handler-Ms": f"{unexplained_inside_handler_ms:.3f}",
                    "X-DTM-Outer-Unexplained-After-Handler-Ms": f"{unexplained_after_handler_ms:.3f}",
                    "X-DTM-Outer-Access-Mode": access_mode,
                    "X-DTM-Outer-Cache-Result": cache_result,
                    "X-DTM-Outer-Route": route,
                    "X-DTM-Outer-Router-Handler-Name": router_handler_name,
                },
            )
        response["headers"] = headers
        return response

    def _should_trace_direct_frontend(self, operation: str) -> bool:
        return is_stage_metrics_enabled(self._ctx) and normalize_path(operation) == "/api/v2/frontend"

    async def handle(self, event: dict[str, Any], request_payload: dict[str, Any], is_http_event: bool) -> dict[str, Any]:
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        with managed_metrics_scope(metrics):
            started_at = perf_counter()
            response: dict[str, Any] | None = None
            result_label = "success"
            operation = "http"
            if is_http_event:
                operation = normalize_path(http_path(event))
            trace_direct_frontend = self._should_trace_direct_frontend(operation)
            trace_id = new_stage_trace_id() if trace_direct_frontend else ""
            requested_mode = self._requested_mode(event, request_payload, is_http_event)
            if requested_mode in STANDARD_RUN_MODES or is_legacy_mode(requested_mode):
                if is_legacy_mode(requested_mode):
                    response = to_gateway_response(
                        error_response(
                            400,
                            code="unsupported_mode",
                            message="Legacy planner modes are no longer supported in standard runtime.",
                            details={"mode": requested_mode},
                        )
                    )
                    result_label = "unsupported_mode"
                else:
                    force_refresh = extract_force_refresh(
                        event,
                        request_payload,
                        is_http_event,
                        query_params=query_params,
                        parse_bool=parse_bool,
                    )
                    planner_event = request_payload.get("event")
                    runtime_response = await self._runtime_shell.execute(
                        RuntimeExecutionRequest(
                            mode=requested_mode,
                            planner_event=planner_event,
                            dry_run=bool(request_payload.get("dry_run", False)),
                            mock_external=request_payload.get("mock_external"),
                            force_refresh=force_refresh,
                        ),
                        is_http_event=True,
                    )
                    response = to_gateway_response(runtime_response)
                    result_label = "runtime"
                if metrics is not None and is_api_metrics_enabled(self._ctx):
                    metrics.counter("dtm.api.requests_total", labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                    metrics.timing("dtm.api.duration_ms", (perf_counter() - started_at) * 1000.0, labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                if logger is not None:
                    logger.info("api_request_finished", operation=operation, result=result_label, status_code=response.get("statusCode"))
                if trace_direct_frontend and is_direct_api_operation(operation):
                    response = self._finalize_direct_api_outer_response(
                        response=response,
                        operation=operation,
                        trace_id=trace_id,
                        started_at=started_at,
                    )
                return response

            request_build_started = perf_counter()
            req_headers = header_params(event)
            if trace_direct_frontend:
                req_headers = dict(req_headers)
                req_headers["X-DTM-Trace-Id"] = trace_id
            req = HttpRequest(
                method=http_method(event) or "GET",
                path=http_path(event),
                query=query_params(event),
                body=request_payload,
                headers=req_headers,
                raw_event=event,
                is_http_event=is_http_event,
            )
            request_build_ms = (perf_counter() - request_build_started) * 1000.0
            if trace_direct_frontend:
                record_api_outer_stage(
                    self._ctx,
                    trace_id=trace_id,
                    operation=operation,
                    stage="request_build",
                    duration_ms=request_build_ms,
                )
            router_started = perf_counter()
            try:
                http_response = await self._router.dispatch(req)
            except Exception as error:
                print(f"http_dispatch_error={error}")
                response = to_gateway_response(
                    error_response(
                        503,
                        code="http_dispatch_failed",
                        message="HTTP handler execution failed.",
                        details={"errorType": type(error).__name__},
                    )
                )
                result_label = "failed"
                if metrics is not None and is_api_metrics_enabled(self._ctx):
                    metrics.counter("dtm.api.requests_total", labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                    metrics.timing("dtm.api.duration_ms", (perf_counter() - started_at) * 1000.0, labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                if logger is not None:
                    logger.error("api_request_finished", operation=operation, result=result_label, error_type=type(error).__name__)
                return response
            router_total_ms = (perf_counter() - router_started) * 1000.0
            if trace_direct_frontend:
                record_api_outer_stage(
                    self._ctx,
                    trace_id=trace_id,
                    operation=operation,
                    stage="router_total",
                    duration_ms=router_total_ms,
                )
            if http_response is not None:
                post_router_started = perf_counter()
                response_build_started = perf_counter()
                response = to_gateway_response(http_response)
                response_build_ms = (perf_counter() - response_build_started) * 1000.0
                result_label = "routed"
                if trace_direct_frontend and is_direct_api_operation(operation):
                    record_api_outer_stage(
                        self._ctx,
                        trace_id=trace_id,
                        operation=operation,
                        stage="response_build",
                        duration_ms=response_build_ms,
                    )
                    router_headers = dict(response.get("headers", {}) or {})
                    router_precheck_ms = self._header_float(router_headers, "X-DTM-Router-Precheck-Ms")
                    router_handler_ms = self._header_float(router_headers, "X-DTM-Router-Handler-Ms")
                    router_handler_name = str(router_headers.get("X-DTM-Router-Handler-Name", "")).strip() or "unknown"
                    post_router_ms = (perf_counter() - post_router_started) * 1000.0
                    record_api_outer_stage(
                        self._ctx,
                        trace_id=trace_id,
                        operation=operation,
                        stage="router_precheck_total",
                        duration_ms=router_precheck_ms,
                        debug_fields={"handler": router_handler_name},
                    )
                    record_api_outer_stage(
                        self._ctx,
                        trace_id=trace_id,
                        operation=operation,
                        stage="router_handler_total",
                        duration_ms=router_handler_ms,
                        debug_fields={"handler": router_handler_name},
                    )
                    record_api_outer_stage(
                        self._ctx,
                        trace_id=trace_id,
                        operation=operation,
                        stage="http_shell_post_router",
                        duration_ms=post_router_ms,
                        debug_fields={"handler": router_handler_name},
                    )
                    response_headers = dict(response.get("headers", {}) or {})
                    frontend_trace_id = str(response_headers.get("X-DTM-Trace-Id", "")).strip() or trace_id
                    frontend_handler_ms = self._header_float(response_headers, "X-DTM-Frontend-Handler-Ms")
                    frontend_inner_ms = self._header_float(response_headers, "X-DTM-Frontend-Inner-Ms")
                    route = str(response_headers.get("X-DTM-Frontend-Route", "")).strip() or "api"
                    access_mode = str(response_headers.get("X-DTM-Frontend-Access-Mode", "")).strip() or "masked"
                    cache_result = str(response_headers.get("X-DTM-Frontend-Cache-Result", "")).strip() or "unknown"
                    response_headers = self._pop_response_headers(
                        response_headers,
                        "X-DTM-Router-Handler-Name",
                        "X-DTM-Router-Precheck-Ms",
                        "X-DTM-Router-Handler-Ms",
                        "X-DTM-Router-Total-Ms",
                        "X-DTM-Trace-Id",
                        "X-DTM-Frontend-Handler-Ms",
                        "X-DTM-Frontend-Inner-Ms",
                        "X-DTM-Frontend-Route",
                        "X-DTM-Frontend-Access-Mode",
                        "X-DTM-Frontend-Cache-Result",
                    )
                    response_headers = append_response_headers(
                        response_headers,
                        {
                            "Server-Timing": build_server_timing_header(
                                {
                                    "router_precheck": router_precheck_ms,
                                    "router_handler": router_handler_ms,
                                    "router_total": router_total_ms,
                                    "http_shell_post_router": post_router_ms,
                                    "response_build": response_build_ms,
                                    "frontend_handler": frontend_handler_ms,
                                    "frontend_inner": frontend_inner_ms,
                                }
                            ),
                            "X-DTM-Outer-Trace-Id": frontend_trace_id,
                            "X-DTM-Outer-Router-Precheck-Ms": f"{router_precheck_ms:.3f}",
                            "X-DTM-Outer-Router-Handler-Ms": f"{router_handler_ms:.3f}",
                            "X-DTM-Outer-Router-Total-Ms": f"{router_total_ms:.3f}",
                            "X-DTM-Outer-Http-Shell-Post-Router-Ms": f"{post_router_ms:.3f}",
                            "X-DTM-Outer-Response-Build-Ms": f"{response_build_ms:.3f}",
                            "X-DTM-Outer-Frontend-Handler-Ms": f"{frontend_handler_ms:.3f}",
                            "X-DTM-Outer-Frontend-Inner-Ms": f"{frontend_inner_ms:.3f}",
                            "X-DTM-Outer-Access-Mode": access_mode,
                            "X-DTM-Outer-Cache-Result": cache_result,
                            "X-DTM-Outer-Route": route,
                            "X-DTM-Outer-Router-Handler-Name": router_handler_name,
                            "X-DTM-Outer-Request-Build-Ms": f"{request_build_ms:.3f}",
                        },
                    )
                    if str(self._ctx.cfg.runtime.runtime.bottleneck_metrics_level or "").strip().lower() == "debug":
                        response_headers = append_response_headers(
                            response_headers,
                            {
                                "X-DTM-Outer-Frontend-Handler-Ms": f"{frontend_handler_ms:.3f}",
                                "X-DTM-Outer-Frontend-Inner-Ms": f"{frontend_inner_ms:.3f}",
                            },
                        )
                    response["headers"] = response_headers
                if metrics is not None and is_api_metrics_enabled(self._ctx):
                    metrics.counter("dtm.api.requests_total", labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                    metrics.timing("dtm.api.duration_ms", (perf_counter() - started_at) * 1000.0, labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                    body = response.get("body", "")
                    metrics.gauge("dtm.api.response_size_bytes", float(len(str(body or "").encode("utf-8"))), labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                if logger is not None:
                    logger.info("api_request_finished", operation=operation, result=result_label, status_code=response.get("statusCode"))
                if trace_direct_frontend and is_direct_api_operation(operation):
                    response = self._finalize_direct_api_outer_response(
                        response=response,
                        operation=operation,
                        trace_id=trace_id,
                        started_at=started_at,
                    )
                return response

            debug_http_shape(
                event,
                is_http_event,
                debug_enabled=self._debug_http_event,
                http_method=http_method,
                http_path=http_path,
                normalize_path=normalize_path,
                query_params=query_params,
            )
            run_mode = extract_run_mode(
                event,
                request_payload,
                is_http_event,
                allowed_run_modes=STANDARD_RUN_MODES,
                query_params=query_params,
            )
            if not run_mode:
                response = to_gateway_response(
                    json_response(
                        200,
                        {
                            "artifact": "dtm_runtime_noop",
                            "message": "HTTP request does not trigger planner without explicit mode.",
                            "allowed_modes": sorted(STANDARD_RUN_MODES),
                        },
                    )
                )
                result_label = "noop"
                if metrics is not None and is_api_metrics_enabled(self._ctx):
                    metrics.counter("dtm.api.requests_total", labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                    metrics.timing("dtm.api.duration_ms", (perf_counter() - started_at) * 1000.0, labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                if logger is not None:
                    logger.info("api_request_finished", operation=operation, result=result_label, status_code=response.get("statusCode"))
                return response

            force_refresh = extract_force_refresh(
                event,
                request_payload,
                is_http_event,
                query_params=query_params,
                parse_bool=parse_bool,
            )
            planner_event = request_payload.get("event")
            runtime_response = await self._runtime_shell.execute(
                RuntimeExecutionRequest(
                    mode=run_mode,
                    planner_event=planner_event,
                    dry_run=bool(request_payload.get("dry_run", False)),
                    mock_external=request_payload.get("mock_external"),
                    force_refresh=force_refresh,
                ),
                is_http_event=True,
            )
            response = to_gateway_response(runtime_response)
            result_label = "runtime"
            if metrics is not None and is_api_metrics_enabled(self._ctx):
                metrics.counter("dtm.api.requests_total", labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
                metrics.timing("dtm.api.duration_ms", (perf_counter() - started_at) * 1000.0, labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "api", "operation": operation, "result": result_label})
            if logger is not None:
                logger.info("api_request_finished", operation=operation, result=result_label, status_code=response.get("statusCode"))
            return response

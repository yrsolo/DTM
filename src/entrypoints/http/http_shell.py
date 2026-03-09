"""HTTP shell for request parsing, routing, and explicit runtime fallback."""

from __future__ import annotations

from typing import Any

from src.app.context import AppContext
from src.entrypoints.http.debug_utils import debug_http_shape
from src.entrypoints.http.dto import HttpRequest, to_gateway_response
from src.entrypoints.http.event_parser import (
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

    async def handle(self, event: dict[str, Any], request_payload: dict[str, Any], is_http_event: bool) -> dict[str, Any]:
        requested_mode = self._requested_mode(event, request_payload, is_http_event)
        if is_legacy_mode(requested_mode):
            return to_gateway_response(
                error_response(
                    400,
                    code="unsupported_mode",
                    message="Legacy planner modes are no longer supported in standard runtime.",
                    details={"mode": requested_mode},
                )
            )

        if requested_mode in STANDARD_RUN_MODES:
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
            return to_gateway_response(runtime_response)

        req = HttpRequest(
            method=http_method(event) or "GET",
            path=http_path(event),
            query=query_params(event),
            body=request_payload,
            headers=event.get("headers", {}) if isinstance(event.get("headers"), dict) else {},
            raw_event=event,
            is_http_event=is_http_event,
        )
        try:
            http_response = await self._router.dispatch(req)
        except Exception as error:
            print(f"http_dispatch_error={error}")
            return to_gateway_response(
                error_response(
                    503,
                    code="http_dispatch_failed",
                    message="HTTP handler execution failed.",
                    details={"errorType": type(error).__name__},
                )
            )
        if http_response is not None:
            return to_gateway_response(http_response)

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
            return to_gateway_response(
                json_response(
                    200,
                    {
                        "artifact": "dtm_runtime_noop",
                        "message": "HTTP request does not trigger planner without explicit mode.",
                        "allowed_modes": sorted(STANDARD_RUN_MODES),
                    },
                )
            )

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
        return to_gateway_response(runtime_response)

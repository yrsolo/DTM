"""Yandex Cloud entrypoint with thin HTTP/runtime dispatch."""

from __future__ import annotations

from typing import Any

from src.app.bootstrap import build_app_context
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.entrypoints.http.debug_utils import debug_http_shape as _debug_http_shape
from src.entrypoints.http.dto import HttpRequest, to_gateway_response
from src.entrypoints.http.event_parser import extract_payload as _extract_payload
from src.entrypoints.http.event_parser import http_method as _http_method
from src.entrypoints.http.event_parser import http_path as _http_path
from src.entrypoints.http.event_parser import normalize_path as _normalize_path
from src.entrypoints.http.event_parser import query_params as _query_params
from src.entrypoints.http.frontend_query_params import parse_bool as _parse_bool
from src.entrypoints.http.frontend_query_params import parse_window_query as _parse_window_query
from src.entrypoints.http.response_utils import error_response as _error_response
from src.entrypoints.http.response_utils import json_response as _json_response
from src.entrypoints.http.router import HttpRouter
from src.entrypoints.http.runtime_execution import RuntimeExecutionRequest, RuntimeExecutor
from src.entrypoints.http.runtime_mode import extract_force_refresh as _extract_force_refresh
from src.entrypoints.http.runtime_mode import extract_run_mode as _extract_run_mode
from src.entrypoints.http.runtime_mode import resolve_trigger_mode as _resolve_trigger_mode
from src.entrypoints.runtime.planner_runtime_entry import PlannerRuntimeRequest, run_planner_runtime

APP_CONTEXT = build_app_context()
APP_CFG = APP_CONTEXT.cfg
APP_DEPS = APP_CONTEXT.deps
APP_DEBUG_HTTP_EVENT = bool(APP_CFG.runtime.api.get("debug_http_event_default", False))
APP_TRIGGERS = dict(APP_CFG.runtime.triggers)
ALLOWED_RUN_MODES = frozenset({"timer", "morning", "test", "sync-only", "reminders-only", "reminder_v2"})


async def handler(event: Any, _: Any) -> dict[str, Any]:
    """Yandex Cloud handler."""
    request_payload, is_http_event = _extract_payload(event)
    if request_payload.get("healthcheck"):
        return {
            "statusCode": 200,
            "body": "!HEALTHY!",
        }

    event_dict = event if isinstance(event, dict) else {}
    req = HttpRequest(
        method=_http_method(event_dict) or "GET",
        path=_http_path(event_dict),
        query=_query_params(event_dict),
        body=request_payload,
        headers=event_dict.get("headers", {}) if isinstance(event_dict.get("headers"), dict) else {},
        raw_event=event_dict,
        is_http_event=is_http_event,
    )

    router = HttpRouter(APP_CONTEXT, frontend_readmodel_repo_cls=FrontendReadmodelRepo)
    try:
        http_response = await router.dispatch(req)
    except Exception as error:
        print(f"http_dispatch_error={error}")
        return to_gateway_response(
            _error_response(
                503,
                code="http_dispatch_failed",
                message="HTTP handler execution failed.",
                details={"errorType": type(error).__name__},
            )
        )
    if http_response is not None:
        return to_gateway_response(http_response)

    _debug_http_shape(
        event_dict,
        is_http_event,
        debug_enabled=APP_DEBUG_HTTP_EVENT,
        http_method=_http_method,
        http_path=_http_path,
        normalize_path=_normalize_path,
        query_params=_query_params,
    )
    run_mode = _extract_run_mode(
        event_dict,
        request_payload,
        is_http_event,
        allowed_run_modes=ALLOWED_RUN_MODES,
        query_params=_query_params,
    )
    trigger_mode = _resolve_trigger_mode(event_dict, APP_TRIGGERS)
    if not run_mode and trigger_mode:
        run_mode = trigger_mode
    if is_http_event and not run_mode:
        return to_gateway_response(
            _json_response(
                200,
                {
                    "artifact": "dtm_runtime_noop",
                    "message": "HTTP request does not trigger planner without explicit mode.",
                    "allowed_modes": sorted(ALLOWED_RUN_MODES),
                },
            )
        )
    if not is_http_event and not run_mode:
        return {
            "statusCode": 200,
            "body": "!NOOP!",
        }

    dry_run = bool(request_payload.get("dry_run", False))
    mock_external = request_payload.get("mock_external")
    force_refresh = _extract_force_refresh(
        event_dict,
        request_payload,
        is_http_event,
        query_params=_query_params,
        parse_bool=_parse_bool,
    )
    planner_event = request_payload.get("event")
    if planner_event is None and not is_http_event:
        planner_event = event

    runtime_request = RuntimeExecutionRequest(
        mode=run_mode,
        planner_event=planner_event,
        dry_run=dry_run,
        mock_external=mock_external,
        force_refresh=force_refresh,
    )
    runtime_response = await RuntimeExecutor(APP_CONTEXT).execute(
        runtime_request,
        main_func=run_planner_runtime,
        request_factory=PlannerRuntimeRequest,
        is_http_event=is_http_event,
    )
    return to_gateway_response(runtime_response)

"""Yandex Cloud entrypoint with planner and group-query handling."""

from __future__ import annotations

from typing import Any

from src.adapters.telegram import TelegramNotifier
from src.app.bootstrap import build_app_context
from src.app.planner_bootstrap import build_planner_dependencies
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.entrypoints.http.event_parser import extract_payload as _extract_payload
from src.entrypoints.http.event_parser import http_method as _http_method
from src.entrypoints.http.event_parser import http_path as _http_path
from src.entrypoints.http.debug_utils import debug_http_shape as _debug_http_shape
from src.entrypoints.http.group_query_handler import (
    GroupQueryHandlerContext,
    GroupQueryHandlerRequest,
    handle_group_query_if_requested,
)
from src.entrypoints.http.group_query_tasks_loader import (
    load_work_tasks_for_group_query as _load_work_tasks_for_group_query,
)
from src.entrypoints.http.event_parser import normalize_path as _normalize_path
from src.entrypoints.http.event_parser import query_params as _query_params
from src.entrypoints.http.frontend_query_params import (
    parse_bool as _parse_bool,
    parse_limit as _parse_limit,
    parse_statuses as _parse_statuses,
    parse_window_query as _parse_window_query,
)
from src.entrypoints.http.runtime_mode import (
    extract_force_refresh as _extract_force_refresh,
    extract_run_mode as _extract_run_mode,
    resolve_trigger_mode as _resolve_trigger_mode,
)
from src.entrypoints.http.runtime_execution import (
    RuntimeExecutionContext,
    RuntimeExecutionRequest,
    execute_runtime,
)
from src.entrypoints.runtime.planner_runtime_entry import PlannerRuntimeRequest, run_planner_runtime
from src.entrypoints.http.response_utils import (
    error_response as _error_response,
    html_response as _html_response,
    json_response as _json_response,
    path_matches as _path_matches,
)
from src.entrypoints.http.frontend_v2_docs import frontend_api_v2_doc, frontend_api_v2_doc_html
from src.entrypoints.http.router import HttpRouter, HttpRouterContext
from src.legacy.http_core_bindings import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)
from src.services.errors import AppError, PermanentError, TransientError, UserError

APP_CONTEXT = build_app_context()
APP_CFG = APP_CONTEXT.cfg
APP_DEPS = APP_CONTEXT.deps
APP_RUNTIME_ENV = APP_CFG.runtime.runtime.env_default
APP_SOURCE_SHEET_NAME = str(APP_CFG.tables.google_sheets.get("source_sheet_name_default", ""))
APP_DEBUG_HTTP_EVENT = bool(APP_CFG.runtime.api.get("debug_http_event_default", False))
APP_TRIGGERS = dict(APP_CFG.runtime.triggers)
APP_TG_BOT_TOKEN = str(APP_DEPS.get("tg_bot_token", ""))
APP_TG_BOT_USERNAME = str(APP_DEPS.get("tg_bot_username", ""))
APP_TG_DEFAULT_CHAT_ID = APP_DEPS.get("default_chat_id")
APP_KEY_JSON = str(APP_DEPS.get("key_json", ""))
APP_SHEET_INFO = dict(APP_DEPS.get("sheet_info", {}))
APP_YDB_ENDPOINT = str(APP_DEPS.get("ydb_endpoint", ""))
APP_YDB_DATABASE = str(APP_DEPS.get("ydb_database", ""))
APP_YDB_SA_JSON_CREDENTIALS = APP_DEPS.get("ydb_sa_json_credentials")
APP_YDB_SA_KEY_FILE = APP_DEPS.get("ydb_sa_key_file")

ALLOWED_RUN_MODES = frozenset({"timer", "morning", "test", "sync-only", "reminders-only"})


async def handler(event: Any, _: Any) -> dict[str, Any]:
    """Yandex Cloud handler."""
    request_payload, is_http_event = _extract_payload(event)
    if request_payload.get("healthcheck"):
        return {
            "statusCode": 200,
            "body": "!HEALTHY!",
        }

    group_query_ctx = GroupQueryHandlerContext(
        bot_username=APP_TG_BOT_USERNAME,
        parse_group_query_request=parse_group_query_request,
        notifier_factory=lambda: TelegramNotifier(
            bot_token=APP_TG_BOT_TOKEN,
            default_chat_id=APP_TG_DEFAULT_CHAT_ID,
        ),
        load_work_tasks_for_group_query=lambda: _load_work_tasks_for_group_query(
            key_json=APP_KEY_JSON,
            sheet_info=APP_SHEET_INFO,
            app_cfg=APP_CFG,
            build_planner_dependencies=build_planner_dependencies,
        ),
        build_deadlines_reply=build_deadlines_reply,
        build_tasks_reply=build_tasks_reply,
    )
    group_query_request = GroupQueryHandlerRequest(
        request_payload=request_payload,
        is_http_event=is_http_event,
    )
    if await handle_group_query_if_requested(group_query_ctx, group_query_request):
        return {
            "statusCode": 200,
            "body": "!GROUP_QUERY_OK!",
        }

    event_dict = event if isinstance(event, dict) else {}
    router_ctx = HttpRouterContext(
        json_response=_json_response,
        html_response=_html_response,
        error_response=_error_response,
        normalize_path=_normalize_path,
        http_path=_http_path,
        http_method=_http_method,
        query_params=_query_params,
        path_matches=_path_matches,
        parse_statuses=_parse_statuses,
        parse_limit=_parse_limit,
        parse_bool=_parse_bool,
        parse_window_query=_parse_window_query,
        ydb_endpoint=APP_YDB_ENDPOINT,
        ydb_database=APP_YDB_DATABASE,
        ydb_sa_json_credentials=APP_YDB_SA_JSON_CREDENTIALS,
        ydb_sa_key_file=APP_YDB_SA_KEY_FILE,
        app_runtime_env=APP_RUNTIME_ENV,
        app_source_sheet_name=APP_SOURCE_SHEET_NAME,
        frontend_api_v2_doc=frontend_api_v2_doc,
        frontend_api_v2_doc_html=frontend_api_v2_doc_html,
        frontend_readmodel_repo_cls=FrontendReadmodelRepo,
    )
    router = HttpRouter(router_ctx)
    try:
        http_response = router.dispatch(event_dict, is_http_event)
    except Exception as error:
        print(f"http_dispatch_error={error}")
        return _error_response(
            503,
            code="http_dispatch_failed",
            message="HTTP handler execution failed.",
            details={"errorType": type(error).__name__},
        )
    if http_response is not None:
        return http_response

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
        return _json_response(
            200,
            {
                "artifact": "dtm_runtime_noop",
                "message": "HTTP request does not trigger planner without explicit mode.",
                "allowed_modes": sorted(ALLOWED_RUN_MODES),
            },
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

    runtime_ctx = RuntimeExecutionContext(
        main_func=run_planner_runtime,
        runtime_request_factory=PlannerRuntimeRequest,
        is_http_event=is_http_event,
        app_error_cls=AppError,
        user_error_cls=UserError,
        transient_error_cls=TransientError,
        permanent_error_cls=PermanentError,
        error_response=_error_response,
        notifier_factory=lambda: TelegramNotifier(
            bot_token=APP_TG_BOT_TOKEN,
            default_chat_id=APP_TG_DEFAULT_CHAT_ID,
        ),
    )
    runtime_request = RuntimeExecutionRequest(
        mode=run_mode,
        planner_event=planner_event,
        dry_run=dry_run,
        mock_external=mock_external,
        force_refresh=force_refresh,
    )
    return await execute_runtime(runtime_ctx, runtime_request)

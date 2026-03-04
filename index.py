"""Yandex Cloud entrypoint with planner and group-query handling."""

from __future__ import annotations

import traceback
from typing import Any

from config import (
    DEFAULT_CHAT_ID,
    KEY_JSON,
    SHEET_INFO,
    TG,
    TG_BOT_USERNAME,
    YC_SA_JSON_CREDENTIALS,
    YC_SA_KEY_FILE,
    YDB_DATABASE,
    YDB_ENDPOINT,
)
from core.api_payload_v2 import build_frontend_api_payload_v2
from core.group_query import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)
from core.reminder import TelegramNotifier
from main import main
from src.app.bootstrap import build_app_context
from src.app.planner_bootstrap import build_planner_dependencies
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.adapters.ydb.task_repository import YdbOperationalTaskRepository
from src.entrypoints.http.event_parser import extract_payload as _extract_payload
from src.entrypoints.http.event_parser import http_method as _http_method
from src.entrypoints.http.event_parser import http_path as _http_path
from src.entrypoints.http.debug_utils import debug_http_shape as _debug_http_shape
from src.entrypoints.http.group_query_handler import handle_group_query_if_requested
from src.entrypoints.http.group_query_tasks_loader import (
    load_work_tasks_for_group_query as _load_work_tasks_for_group_query,
)
from src.entrypoints.http.event_parser import normalize_path as _normalize_path
from src.entrypoints.http.event_parser import query_params as _query_params
from src.entrypoints.http.frontend_compat_handlers import handle_frontend_api_root_if_requested
from src.entrypoints.http.frontend_query_params import (
    parse_bool as _parse_bool,
    parse_limit as _parse_limit,
    parse_statuses as _parse_statuses,
    parse_window_query as _parse_window_query,
)
from src.entrypoints.http.frontend_tasks_loader import load_frontend_tasks as _load_frontend_tasks
from src.entrypoints.http.runtime_mode import (
    extract_force_refresh as _extract_force_refresh,
    extract_run_mode as _extract_run_mode,
    resolve_trigger_mode as _resolve_trigger_mode,
)
from src.entrypoints.http.response_utils import (
    error_response as _error_response,
    html_response as _html_response,
    json_response as _json_response,
    path_matches as _path_matches,
)
from src.entrypoints.http.frontend_v2_docs import frontend_api_v2_doc, frontend_api_v2_doc_html
from src.entrypoints.http.frontend_v2_handler import handle_frontend_api_v2_if_requested
from src.entrypoints.http.router import dispatch_http
from src.services.errors import AppError, PermanentError, TransientError, UserError

APP_CONTEXT = build_app_context()
APP_CFG = APP_CONTEXT.cfg
APP_RUNTIME_ENV = APP_CFG.runtime.runtime.env_default
APP_SOURCE_SHEET_NAME = str(APP_CFG.tables.google_sheets.get("source_sheet_name_default", ""))
APP_READMODEL_SOURCE = APP_CFG.runtime.sources.readmodel_source_default
APP_DEBUG_HTTP_EVENT = bool(APP_CFG.runtime.api.get("debug_http_event_default", False))
APP_TRIGGERS = dict(APP_CFG.runtime.triggers)
APP_TG_BOT_TOKEN = TG
APP_TG_DEFAULT_CHAT_ID = DEFAULT_CHAT_ID

ALLOWED_RUN_MODES = frozenset({"timer", "morning", "test", "sync-only", "reminders-only"})


def _handle_frontend_api_v2_if_requested(
    event: dict[str, Any], is_http_event: bool
) -> dict[str, Any] | None:
    return handle_frontend_api_v2_if_requested(
        event,
        is_http_event,
        json_response=_json_response,
        html_response=_html_response,
        error_response=_error_response,
        normalize_path=_normalize_path,
        http_path=_http_path,
        http_method=_http_method,
        query_params=_query_params,
        path_matches=lambda path, candidates: _path_matches(path, candidates, _normalize_path),
        parse_statuses=_parse_statuses,
        parse_limit=_parse_limit,
        parse_bool=_parse_bool,
        parse_window_query=_parse_window_query,
        app_readmodel_source=APP_READMODEL_SOURCE,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        ydb_sa_json_credentials=YC_SA_JSON_CREDENTIALS,
        ydb_sa_key_file=YC_SA_KEY_FILE,
        app_runtime_env=APP_RUNTIME_ENV,
        app_source_sheet_name=APP_SOURCE_SHEET_NAME,
        key_json=KEY_JSON,
        sheet_info=SHEET_INFO,
        app_cfg=APP_CFG,
        frontend_api_v2_doc=frontend_api_v2_doc,
        frontend_api_v2_doc_html=frontend_api_v2_doc_html,
        frontend_readmodel_repo_cls=FrontendReadmodelRepo,
        build_planner_dependencies=build_planner_dependencies,
        load_frontend_tasks=lambda dependencies, statuses: _load_frontend_tasks(
            dependencies,
            statuses,
            app_readmodel_source=APP_READMODEL_SOURCE,
            ydb_endpoint=YDB_ENDPOINT,
            ydb_database=YDB_DATABASE,
            ydb_sa_json_credentials=YC_SA_JSON_CREDENTIALS,
            ydb_sa_key_file=YC_SA_KEY_FILE,
            ydb_operational_task_repo_cls=YdbOperationalTaskRepository,
        ),
        build_frontend_api_payload_v2=build_frontend_api_payload_v2,
    )


def _handle_api_root_if_requested(
    event: dict[str, Any], is_http_event: bool
) -> dict[str, Any] | None:
    return handle_frontend_api_root_if_requested(
        event,
        is_http_event,
        json_response=_json_response,
        html_response=_html_response,
        normalize_path=_normalize_path,
        http_path=_http_path,
        http_method=_http_method,
        query_params=_query_params,
        frontend_api_v2_doc=frontend_api_v2_doc,
        frontend_api_v2_doc_html=frontend_api_v2_doc_html,
    )


async def handler(event: Any, _: Any) -> dict[str, Any]:
    """Yandex Cloud handler."""
    request_payload, is_http_event = _extract_payload(event)
    if request_payload.get("healthcheck"):
        return {
            "statusCode": 200,
            "body": "!HEALTHY!",
        }

    if await handle_group_query_if_requested(
        request_payload,
        is_http_event,
        bot_username=TG_BOT_USERNAME,
        parse_group_query_request=parse_group_query_request,
        notifier_factory=lambda: TelegramNotifier(
            bot_token=APP_TG_BOT_TOKEN,
            default_chat_id=APP_TG_DEFAULT_CHAT_ID,
        ),
        load_work_tasks_for_group_query=lambda: _load_work_tasks_for_group_query(
            key_json=KEY_JSON,
            sheet_info=SHEET_INFO,
            app_cfg=APP_CFG,
            build_planner_dependencies=build_planner_dependencies,
        ),
        build_deadlines_reply=build_deadlines_reply,
        build_tasks_reply=build_tasks_reply,
    ):
        return {
            "statusCode": 200,
            "body": "!GROUP_QUERY_OK!",
        }

    event_dict = event if isinstance(event, dict) else {}
    http_response = dispatch_http(
        event_dict,
        is_http_event,
        (
            _handle_api_root_if_requested,
            _handle_frontend_api_v2_if_requested,
        ),
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

    try:
        await main(
            event=planner_event,
            mode=run_mode,
            dry_run=dry_run,
            mock_external=mock_external,
            force_refresh=force_refresh,
        )
    except Exception as ex:
        if isinstance(ex, UserError):
            error_family = "user"
        elif isinstance(ex, TransientError):
            error_family = "transient"
        elif isinstance(ex, PermanentError):
            error_family = "permanent"
        elif isinstance(ex, AppError):
            error_family = "app"
        else:
            error_family = "unknown"
        tr = str(traceback.format_exc())
        txt = f"Runtime failure:\n{ex}\nTRACEBACK\n{tr}\n"

        print(f"runtime_error_classification={error_family}")
        if isinstance(ex, AppError) and is_http_event:
            status_code = 500
            if isinstance(ex, UserError):
                status_code = 400
            elif isinstance(ex, TransientError):
                status_code = 503
            return _error_response(
                status_code,
                code=ex.code,
                message=str(ex),
            )
        print(txt)
        try:
            await TelegramNotifier(
                bot_token=APP_TG_BOT_TOKEN,
                default_chat_id=APP_TG_DEFAULT_CHAT_ID,
            ).alog(txt)
        except Exception as notifier_error:
            print(f"Error notifier failed: {notifier_error}")

        return {
            "statusCode": 200,
            "body": "!!!EGGORR!!!",
        }

    return {
        "statusCode": 200,
        "body": "!GOOD!",
    }

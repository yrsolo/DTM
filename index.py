"""Yandex Cloud entrypoint with planner and group-query handling."""

from __future__ import annotations

import json
import traceback
from datetime import datetime
from typing import Any

from config import (
    DEFAULT_CHAT_ID,
    KEY_JSON,
    SHEET_INFO,
    TG,
    TG_BOT_USERNAME,
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
from src.entrypoints.http.event_parser import normalize_path as _normalize_path
from src.entrypoints.http.event_parser import query_params as _query_params
from src.entrypoints.http.frontend_v2_docs import frontend_api_v2_doc, frontend_api_v2_doc_html
from src.entrypoints.http.frontend_v2_handler import handle_frontend_api_v2_if_requested
from src.entrypoints.http.router import dispatch_http
from src.services.errors import AppError, PermanentError, TransientError, UserError
from src.services.source_policy import build_source_policy_matrix

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

def _load_work_tasks_for_group_query() -> list[Any]:
    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=True,
        mock_external=True,
        cfg=APP_CFG,
    )
    return dependencies.task_repository.get_task_by_color_status(["work", "pre_done"])


async def _handle_group_query_if_requested(
    request_payload: dict[str, Any], is_http_event: bool
) -> bool:
    if not is_http_event:
        return False

    query = parse_group_query_request(request_payload, bot_username=TG_BOT_USERNAME)
    if query is None:
        return False

    notifier = TelegramNotifier(bot_token=APP_TG_BOT_TOKEN, default_chat_id=APP_TG_DEFAULT_CHAT_ID)
    try:
        tasks = _load_work_tasks_for_group_query()
        if query.action == "deadlines":
            reply = build_deadlines_reply(tasks)
        else:
            reply = build_tasks_reply(tasks, requester_name=query.requester_name)
        await notifier.send_message(query.chat_id, reply, parse_mode=None)
        return True
    except Exception as error:
        print(f"group_query_error={error}")
        await notifier.send_message(
            query.chat_id,
            "Не смогла собрать список задач. Попробуйте еще раз через минуту.",
            parse_mode=None,
        )
        return True


def _json_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False),
    }


def _error_response(
    status_code: int, *, code: str, message: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    return _json_response(
        status_code,
        {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


def _debug_http_shape(event: dict[str, Any], is_http_event: bool) -> None:
    if not APP_DEBUG_HTTP_EVENT:
        return
    if not isinstance(event, dict):
        print("api_debug non_dict_event")
        return
    request_context = event.get("requestContext")
    rc_keys = sorted(request_context.keys()) if isinstance(request_context, dict) else []
    params = event.get("params")
    params_keys = sorted(params.keys()) if isinstance(params, dict) else []
    qs = _query_params(event)
    print(
        "api_debug "
        f"is_http={is_http_event} "
        f"method={_http_method(event)!r} "
        f"path={_http_path(event)!r} "
        f"norm_path={_normalize_path(_http_path(event))!r} "
        f"event_keys={sorted(event.keys())} "
        f"request_context_keys={rc_keys} "
        f"params_keys={params_keys} "
        f"query_keys={sorted(qs.keys()) if isinstance(qs, dict) else []}"
    )


def _html_response(status_code: int, html: str) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "body": html,
    }


def _resolve_trigger_mode(event: Any) -> str:
    try:
        messages = event.get("messages")
        trigger_id = str(messages[0]["details"]["trigger_id"]).strip()
    except (TypeError, KeyError, IndexError):
        return ""
    return str(APP_TRIGGERS.get(trigger_id, "")).strip().lower()


def _parse_statuses(raw: str) -> list[str]:
    items = [part.strip() for part in str(raw or "").split(",") if part.strip()]
    return items or ["work", "pre_done"]


def _parse_limit(raw: str, default: int = 200) -> int:
    try:
        value = int(str(raw or default))
    except ValueError:
        value = default
    return max(1, min(value, 1000))


def _parse_bool(raw: str, default: bool = True) -> bool:
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "y"}


def _parse_window_query(params: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    window_start_raw = str(params.get("window_start", "")).strip()
    window_end_raw = str(params.get("window_end", "")).strip()
    window_mode = str(params.get("window_mode", "")).strip() or "intersects"

    if not window_start_raw and not window_end_raw:
        return (
            {
                "enabled": False,
                "start": None,
                "end": None,
                "mode": window_mode,
            },
            None,
        )

    if not window_start_raw or not window_end_raw:
        return {}, {
            "code": "invalid_window",
            "message": "Both window_start and window_end are required when window is enabled.",
            "details": {
                "window_start": window_start_raw or None,
                "window_end": window_end_raw or None,
            },
        }

    if window_mode != "intersects":
        return {}, {
            "code": "invalid_window",
            "message": "Unsupported window_mode. Allowed value: intersects.",
            "details": {"window_mode": window_mode},
        }

    try:
        window_start = datetime.strptime(window_start_raw, "%Y-%m-%d").date()
        window_end = datetime.strptime(window_end_raw, "%Y-%m-%d").date()
    except ValueError:
        return {}, {
            "code": "invalid_window",
            "message": "window_start/window_end must use YYYY-MM-DD format.",
            "details": {
                "window_start": window_start_raw,
                "window_end": window_end_raw,
            },
        }

    if window_start > window_end:
        return {}, {
            "code": "invalid_window",
            "message": "window_start must be less than or equal to window_end.",
            "details": {
                "window_start": window_start_raw,
                "window_end": window_end_raw,
            },
        }

    return (
        {
            "enabled": True,
            "start": window_start,
            "end": window_end,
            "mode": window_mode,
        },
        None,
    )


def _load_frontend_tasks(dependencies: Any, statuses: list[str]) -> list[Any]:
    policy = build_source_policy_matrix(
        readmodel_source=APP_READMODEL_SOURCE,
        notify_source="legacy",
        render_source="legacy",
    )
    if not policy.api_reads_ydb():
        return dependencies.task_repository.get_task_by_color_status(statuses)
    task_repo = YdbOperationalTaskRepository(endpoint=YDB_ENDPOINT, database=YDB_DATABASE)
    return task_repo.get_task_by_color_status(statuses)


def _extract_run_mode(
    event: dict[str, Any],
    request_payload: dict[str, Any],
    is_http_event: bool,
) -> str:
    raw_mode = str(request_payload.get("mode", "")).strip().lower()
    if not raw_mode and is_http_event:
        params = _query_params(event)
        raw_mode = str(params.get("mode", "")).strip().lower()
    if raw_mode not in ALLOWED_RUN_MODES:
        return ""
    return raw_mode


def _extract_force_refresh(
    event: dict[str, Any],
    request_payload: dict[str, Any],
    is_http_event: bool,
) -> bool:
    payload_value = request_payload.get("force_refresh")
    if payload_value is not None:
        return _parse_bool(str(payload_value), default=False)
    if is_http_event:
        params = _query_params(event)
        return _parse_bool(params.get("force_refresh"), default=False)
    return False


def _path_matches(path: str, candidates: set[str]) -> bool:
    normalized = _normalize_path(path)
    if normalized in candidates:
        return True
    return any(normalized.endswith(candidate) for candidate in candidates)


def _handle_frontend_api_if_requested(
    event: dict[str, Any], is_http_event: bool
) -> dict[str, Any] | None:
    if not is_http_event:
        return None
    path = _normalize_path(_http_path(event))
    method = _http_method(event) or "GET"
    if method == "ANY":
        method = "GET"
    if method != "GET":
        return None

    v1_paths = {
        "/api/v1",
        "/api/v1/frontend",
        "/api/v1/read-model",
        "/api/v1/frontend/doc",
        "/api/v1/read-model/doc",
    }
    if not _path_matches(path, v1_paths):
        return None

    return _error_response(
        410,
        code="api_v1_discontinued",
        message="API v1 is discontinued. Use /api/v2/frontend and /api/v2/frontend/doc.",
    )


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
        path_matches=_path_matches,
        parse_statuses=_parse_statuses,
        parse_limit=_parse_limit,
        parse_bool=_parse_bool,
        parse_window_query=_parse_window_query,
        app_readmodel_source=APP_READMODEL_SOURCE,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        app_runtime_env=APP_RUNTIME_ENV,
        app_source_sheet_name=APP_SOURCE_SHEET_NAME,
        key_json=KEY_JSON,
        sheet_info=SHEET_INFO,
        app_cfg=APP_CFG,
        frontend_api_v2_doc=frontend_api_v2_doc,
        frontend_api_v2_doc_html=frontend_api_v2_doc_html,
        frontend_readmodel_repo_cls=FrontendReadmodelRepo,
        build_planner_dependencies=build_planner_dependencies,
        load_frontend_tasks=_load_frontend_tasks,
        build_frontend_api_payload_v2=build_frontend_api_payload_v2,
    )


def _handle_api_root_if_requested(
    event: dict[str, Any], is_http_event: bool
) -> dict[str, Any] | None:
    if not is_http_event:
        return None
    method = _http_method(event) or "GET"
    if method == "ANY":
        method = "GET"
    if method != "GET":
        return None
    path = _normalize_path(_http_path(event))
    if path not in {"/"}:
        return None
    params = _query_params(event)
    as_json = str(params.get("format", "")).strip().lower() == "json"
    return (
        _json_response(200, frontend_api_v2_doc())
        if as_json
        else _html_response(200, frontend_api_v2_doc_html())
    )


async def handler(event: Any, _: Any) -> dict[str, Any]:
    """Yandex Cloud handler."""
    request_payload, is_http_event = _extract_payload(event)
    if request_payload.get("healthcheck"):
        return {
            "statusCode": 200,
            "body": "!HEALTHY!",
        }

    if await _handle_group_query_if_requested(request_payload, is_http_event):
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
            _handle_frontend_api_if_requested,
        ),
    )
    if http_response is not None:
        return http_response

    _debug_http_shape(event_dict, is_http_event)
    run_mode = _extract_run_mode(event_dict, request_payload, is_http_event)
    trigger_mode = _resolve_trigger_mode(event_dict)
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
    force_refresh = _extract_force_refresh(event_dict, request_payload, is_http_event)
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



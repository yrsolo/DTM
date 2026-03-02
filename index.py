"""Yandex Cloud entrypoint with planner and group-query handling."""

from __future__ import annotations

import json
import traceback
from typing import Any

from config import KEY_JSON, RUNTIME_ENV, SHEET_INFO, SOURCE_SHEET_NAME, TG_BOT_USERNAME
from core.api_payload import build_frontend_api_payload
from core.bootstrap import build_planner_dependencies
from core.group_query import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)
from core.reminder import TelegramNotifier
from main import main


def _extract_payload(event: Any) -> tuple[dict[str, Any], bool]:
    if not isinstance(event, dict):
        return {}, False
    is_http = any(key in event for key in ("httpMethod", "path", "requestContext", "queryStringParameters"))
    if "body" not in event:
        return event, is_http

    raw_body = event.get("body")
    if isinstance(raw_body, dict):
        return raw_body, True
    if isinstance(raw_body, str) and raw_body.strip():
        try:
            parsed = json.loads(raw_body)
            if isinstance(parsed, dict):
                return parsed, True
        except json.JSONDecodeError:
            pass
    return {}, True


def _load_work_tasks_for_group_query() -> list[Any]:
    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=True,
        mock_external=True,
    )
    return dependencies.task_repository.get_task_by_color_status(["work", "pre_done"])


async def _handle_group_query_if_requested(request_payload: dict[str, Any], is_http_event: bool) -> bool:
    if not is_http_event:
        return False

    query = parse_group_query_request(request_payload, bot_username=TG_BOT_USERNAME)
    if query is None:
        return False

    notifier = TelegramNotifier()
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


def _http_path(event: dict[str, Any]) -> str:
    if not isinstance(event, dict):
        return ""
    request_context = event.get("requestContext")
    if isinstance(request_context, dict):
        http_ctx = request_context.get("http")
        if isinstance(http_ctx, dict):
            return str(http_ctx.get("path", "")).strip()
    return str(event.get("path", "")).strip()


def _http_method(event: dict[str, Any]) -> str:
    if not isinstance(event, dict):
        return ""
    request_context = event.get("requestContext")
    if isinstance(request_context, dict):
        http_ctx = request_context.get("http")
        if isinstance(http_ctx, dict):
            return str(http_ctx.get("method", "")).strip().upper()
    return str(event.get("httpMethod", "")).strip().upper()


def _query_params(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    direct = event.get("queryStringParameters")
    if isinstance(direct, dict):
        return direct
    params = event.get("params")
    if isinstance(params, dict):
        qs = params.get("queryString")
        if isinstance(qs, dict):
            return qs
    return {}


def _json_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False),
    }


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


def _frontend_api_doc() -> dict[str, Any]:
    return {
        "artifact": "dtm_frontend_api_doc",
        "version": "1.0.0",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/v1/frontend",
                "query": {
                    "statuses": "Comma-separated status filter, default: work,pre_done",
                    "designer": "Optional designer exact-name filter (case-insensitive)",
                    "limit": "Optional integer [1..1000], default: 200",
                    "include_people": "Optional bool (1/0,true/false), default: true",
                },
            },
            {"method": "GET", "path": "/api/v1/read-model", "alias_of": "/api/v1/frontend"},
            {"method": "GET", "path": "/api/v1/frontend/doc"},
        ],
        "response_shape": {
            "artifact": "dtm_frontend_api_payload",
            "generated_at_utc": "ISO UTC timestamp",
            "source": {"env": "dev|test|prod", "source_sheet_name": "string"},
            "filters": {"statuses": ["string"], "designer": "string", "limit": 200, "include_people": True},
            "summary": {"tasks_total": 0, "tasks_filtered": 0, "tasks_returned": 0, "people_total": 0},
            "tasks": [
                {
                    "id": "string",
                    "name": "string",
                    "designer": "string",
                    "status": "string",
                    "color_status": "string",
                    "timing": [{"date": "YYYY-MM-DD", "stages": ["string"]}],
                    "next_due_date": "YYYY-MM-DD|null",
                }
            ],
            "deadlines": [{"date": "YYYY-MM-DD", "task_id": "string", "task_name": "string"}],
            "people": [{"id": "string", "name": "string", "position": "string"}],
        },
    }


def _handle_frontend_api_if_requested(event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
    if not is_http_event:
        return None
    path = _http_path(event)
    method = _http_method(event)
    if method != "GET":
        return None

    if path in {"/", "/api", "/api/v1", "/api/v1/frontend/doc", "/api/v1/read-model/doc"}:
        return _json_response(200, _frontend_api_doc())
    if path not in {"/api/v1/frontend", "/api/v1/read-model"}:
        return None

    params = _query_params(event)
    statuses = _parse_statuses(params.get("statuses", "work,pre_done"))
    designer = str(params.get("designer", "")).strip()
    limit = _parse_limit(params.get("limit", "200"))
    include_people = _parse_bool(params.get("include_people"), default=True)

    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=True,
        mock_external=True,
    )
    tasks = dependencies.task_repository.get_task_by_color_status(statuses)
    people = []
    if include_people:
        dependencies.people_manager.get_designers()
        people = list(dependencies.people_manager.people.values())

    payload = build_frontend_api_payload(
        tasks=tasks,
        people=people,
        env_name=RUNTIME_ENV,
        source_sheet_name=SOURCE_SHEET_NAME,
        statuses=statuses,
        limit=limit,
        include_people=include_people,
        designer_filter=designer,
    )
    return _json_response(200, payload)


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

    frontend_response = _handle_frontend_api_if_requested(event if isinstance(event, dict) else {}, is_http_event)
    if frontend_response is not None:
        return frontend_response

    run_mode = request_payload.get("mode")
    dry_run = bool(request_payload.get("dry_run", False))
    mock_external = request_payload.get("mock_external")
    planner_event = request_payload.get("event")
    if planner_event is None and not is_http_event:
        planner_event = event

    try:
        await main(
            event=planner_event,
            mode=run_mode,
            dry_run=dry_run,
            mock_external=mock_external,
        )
    except Exception as ex:
        tr = str(traceback.format_exc())
        txt = f"Runtime failure:\n{ex}\nTRACEBACK\n{tr}\n"

        print(txt)
        try:
            await TelegramNotifier().alog(txt)
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

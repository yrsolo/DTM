"""Yandex Cloud entrypoint with planner and group-query handling."""

from __future__ import annotations

import json
import traceback
from typing import Any

from config import (
    KEY_JSON,
    RUNTIME_ENV,
    SHEET_INFO,
    SOURCE_SHEET_NAME,
    TG_BOT_USERNAME,
    TRIGGERS,
)
from core.api_payload import build_frontend_api_payload
from core.bootstrap import build_planner_dependencies
from core.group_query import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)
from core.reminder import TelegramNotifier
from main import main

ALLOWED_RUN_MODES = frozenset({"timer", "morning", "test", "sync-only", "reminders-only"})


def _extract_payload(event: Any) -> tuple[dict[str, Any], bool]:
    if not isinstance(event, dict):
        return {}, False
    is_http = any(
        key in event
        for key in (
            "httpMethod",
            "method",
            "requestMethod",
            "path",
            "rawPath",
            "raw_path",
            "requestContext",
            "queryStringParameters",
            "rawQueryString",
            "params",
            "url",
        )
    )
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
            path = str(http_ctx.get("path", "")).strip()
            if path:
                return path
            raw_path = str(http_ctx.get("rawPath", "")).strip()
            if raw_path:
                return raw_path
        rc_path = str(request_context.get("path", "")).strip()
        if rc_path:
            return rc_path
    for key in ("path", "rawPath", "raw_path", "url"):
        path = str(event.get(key, "")).strip()
        if path:
            return path
    params = event.get("params")
    if isinstance(params, dict):
        path_map = params.get("path")
        if isinstance(path_map, dict):
            for key in ("proxy", "path"):
                path = str(path_map.get(key, "")).strip()
                if path:
                    return path
    return ""


def _http_method(event: dict[str, Any]) -> str:
    if not isinstance(event, dict):
        return ""
    request_context = event.get("requestContext")
    if isinstance(request_context, dict):
        http_ctx = request_context.get("http")
        if isinstance(http_ctx, dict):
            method = str(http_ctx.get("method", "")).strip().upper()
            if method:
                return method
        method = str(request_context.get("httpMethod", "")).strip().upper()
        if method:
            return method
    for key in ("httpMethod", "method", "requestMethod"):
        method = str(event.get(key, "")).strip().upper()
        if method:
            return method
    return ""


def _query_params(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    direct = event.get("queryStringParameters")
    if isinstance(direct, dict):
        return direct
    raw_query = event.get("rawQueryString")
    if isinstance(raw_query, str) and raw_query.strip():
        parsed: dict[str, Any] = {}
        for pair in raw_query.split("&"):
            if not pair:
                continue
            if "=" in pair:
                key, value = pair.split("=", 1)
            else:
                key, value = pair, ""
            key = key.strip()
            if key:
                parsed[key] = value.strip()
        if parsed:
            return parsed
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
    return str(TRIGGERS.get(trigger_id, "")).strip().lower()


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


def _frontend_api_doc_html() -> str:
    return """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>DTM Frontend API</title>
  <style>
    :root { color-scheme: light; }
    body { margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f6f8fb; color: #17212b; }
    .wrap { max-width: 980px; margin: 0 auto; padding: 24px; }
    .card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,.06); margin-bottom: 16px; }
    h1, h2, h3 { margin: 0 0 10px; }
    p { margin: 8px 0; line-height: 1.45; }
    code { background: #eef2f7; padding: 2px 6px; border-radius: 6px; }
    pre { margin: 0; padding: 12px; background: #0f172a; color: #e2e8f0; border-radius: 10px; overflow: auto; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; border-bottom: 1px solid #e5e7eb; padding: 8px; vertical-align: top; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>DTM Frontend API</h1>
      <p>Версия контракта: <code>1.0.0</code></p>
      <p>Назначение: отдать фронту задачи, дедлайны и людей в одном JSON.</p>
    </div>
    <div class="card">
      <h2>Endpoints</h2>
      <table>
        <thead><tr><th>Method</th><th>Path</th><th>Назначение</th></tr></thead>
        <tbody>
          <tr><td>GET</td><td><code>/api/v1/frontend</code></td><td>Основной payload для UI</td></tr>
          <tr><td>GET</td><td><code>/api/v1/read-model</code></td><td>Alias к <code>/api/v1/frontend</code></td></tr>
          <tr><td>GET</td><td><code>/api/v1/frontend/doc</code></td><td>Эта страница</td></tr>
          <tr><td>GET</td><td><code>/api/v1/frontend/doc?format=json</code></td><td>JSON-док с форматом</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>Query params</h2>
      <table>
        <thead><tr><th>Param</th><th>Тип</th><th>Default</th><th>Описание</th></tr></thead>
        <tbody>
          <tr><td><code>statuses</code></td><td>string</td><td><code>work,pre_done</code></td><td>Фильтр статусов через запятую</td></tr>
          <tr><td><code>designer</code></td><td>string</td><td><code></code></td><td>Фильтр по имени дизайнера (без учета регистра)</td></tr>
          <tr><td><code>limit</code></td><td>int</td><td><code>200</code></td><td>Лимит задач, диапазон 1..1000</td></tr>
          <tr><td><code>include_people</code></td><td>bool</td><td><code>true</code></td><td>Добавлять блок <code>people</code></td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>Пример запроса</h2>
      <pre>GET /api/v1/frontend?statuses=work,pre_done&amp;limit=100&amp;include_people=true</pre>
    </div>
    <div class="card">
      <h2>Ключевые поля ответа</h2>
      <pre>{
  "artifact": "dtm_frontend_api_payload",
  "generated_at_utc": "2026-03-02T19:00:00Z",
  "source": {"env": "test", "source_sheet_name": "Спонсорские ТНТ"},
  "filters": {"statuses": ["work","pre_done"], "designer": "", "limit": 100, "include_people": true},
  "summary": {"tasks_total": 0, "tasks_filtered": 0, "tasks_returned": 0, "people_total": 0},
  "tasks": [{"id": "...", "name": "...", "designer": "...", "next_due_date": "YYYY-MM-DD|null"}],
  "deadlines": [{"date": "YYYY-MM-DD", "task_id": "...", "task_name": "..."}],
  "people": [{"id": "...", "name": "...", "position": "..."}]
}</pre>
    </div>
  </div>
</body>
</html>
"""


def _normalize_path(path: str) -> str:
    value = str(path or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        marker = value.find("/", value.find("://") + 3)
        value = value[marker:] if marker != -1 else "/"
    if "?" in value:
        value = value.split("?", 1)[0]
    if not value.startswith("/"):
        value = "/" + value
    if len(value) > 1 and value.endswith("/"):
        value = value[:-1]
    return value


def _path_matches(path: str, candidates: set[str]) -> bool:
    normalized = _normalize_path(path)
    if normalized in candidates:
        return True
    return any(normalized.endswith(candidate) for candidate in candidates)


def _handle_frontend_api_if_requested(event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
    if not is_http_event:
        return None
    path = _normalize_path(_http_path(event))
    method = _http_method(event)
    if not method:
        # Some API Gateway integrations omit explicit HTTP method in event payload.
        # Browser/API usage for frontend endpoint is read-only GET.
        method = "GET"
    if method == "ANY":
        # Yandex API Gateway with x-yc-apigateway-any-method can pass "ANY" as method.
        # Frontend endpoints are read-only, so treat it as GET.
        method = "GET"
    if method != "GET":
        return None

    params = _query_params(event)
    doc_paths = {"/", "/api", "/api/v1", "/api/v1/frontend/doc", "/api/v1/read-model/doc"}
    data_paths = {"/api/v1/frontend", "/api/v1/read-model"}

    if _path_matches(path, doc_paths):
        if str(params.get("format", "")).strip().lower() == "json":
            return _json_response(200, _frontend_api_doc())
        return _html_response(200, _frontend_api_doc_html())
    if not _path_matches(path, data_paths):
        return None

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

    event_dict = event if isinstance(event, dict) else {}
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

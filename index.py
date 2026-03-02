"""Yandex Cloud entrypoint with planner and group-query handling."""

from __future__ import annotations

import json
import os
import re
import time
import traceback
from typing import Any
from urllib.parse import parse_qsl, urlparse

from config import (
    KEY_JSON,
    FRONTEND_API_DEFAULT_VERSION,
    RUNTIME_ENV,
    SHEET_INFO,
    SOURCE_SHEET_NAME,
    TG_BOT_USERNAME,
    TRIGGERS,
)
from core.api_payload import build_frontend_api_payload
from core.api_payload_v2 import build_frontend_api_payload_v2
from core.bootstrap import build_planner_dependencies
from core.group_query import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)
from core.reminder import TelegramNotifier
from main import main

ALLOWED_RUN_MODES = frozenset({"timer", "morning", "test", "sync-only", "reminders-only"})
DEBUG_HTTP_EVENT = os.getenv("DEBUG_HTTP_EVENT", os.getenv("DEBUG_API_EVENT_SHAPE", "0")).strip().lower() in {
    "1",
    "true",
    "yes",
}


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
    def _normalize_proxy_path(value: Any) -> str:
        raw = str(value or "").strip()
        if not raw:
            return ""
        if raw == "/{proxy+}" or raw == "{proxy+}":
            return ""
        return raw if raw.startswith("/") else f"/{raw}"

    if not isinstance(event, dict):
        return ""
    # Proxy placeholders often carry the real route in pathParams/params.proxy.
    path_params = event.get("pathParams")
    if isinstance(path_params, dict):
        proxy = _normalize_proxy_path(path_params.get("proxy"))
        if proxy:
            return proxy
    params = event.get("params")
    if isinstance(params, dict):
        proxy = _normalize_proxy_path(params.get("proxy"))
        if proxy:
            return proxy
        params_path = _normalize_proxy_path(params.get("path"))
        if params_path:
            return params_path
        path_map = params.get("path")
        if isinstance(path_map, dict):
            for key in ("proxy", "path"):
                path = _normalize_proxy_path(path_map.get(key))
                if path:
                    return path

    request_context = event.get("requestContext")
    if isinstance(request_context, dict):
        http_ctx = request_context.get("http")
        if isinstance(http_ctx, dict):
            path = _normalize_proxy_path(http_ctx.get("path"))
            if path:
                return path
            raw_path = _normalize_proxy_path(http_ctx.get("rawPath"))
            if raw_path:
                return raw_path
        rc_path = _normalize_proxy_path(request_context.get("path"))
        if rc_path:
            return rc_path
    for key in ("path", "rawPath", "raw_path", "url"):
        path = _normalize_proxy_path(event.get(key))
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
    def _flatten(source: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in source.items():
            if isinstance(value, list):
                result[key] = str(value[0]).strip() if value else ""
            elif value is None:
                result[key] = ""
            else:
                result[key] = str(value).strip()
        return result

    if not isinstance(event, dict):
        return {}
    direct = event.get("queryStringParameters")
    if isinstance(direct, dict) and direct:
        return _flatten(direct)
    raw_query = event.get("rawQueryString")
    if isinstance(raw_query, str) and raw_query.strip():
        parsed = {key: value for key, value in parse_qsl(raw_query, keep_blank_values=True)}
        if parsed:
            return parsed
    multi = event.get("multiValueQueryStringParameters")
    if isinstance(multi, dict) and multi:
        return _flatten(multi)
    url = event.get("url")
    if isinstance(url, str) and url.startswith(("http://", "https://")):
        parsed_url = urlparse(url)
        parsed = {key: value for key, value in parse_qsl(parsed_url.query, keep_blank_values=True)}
        if parsed:
            return parsed
    params = event.get("params")
    if isinstance(params, dict):
        qs = params.get("queryString")
        if isinstance(qs, dict):
            flattened = _flatten(qs)
            if flattened:
                return flattened
    multi_params = event.get("multiValueParams")
    if isinstance(multi_params, dict):
        qs = multi_params.get("queryString")
        if isinstance(qs, dict):
            flattened = _flatten(qs)
            if flattened:
                return flattened
    return {}


def _json_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False),
    }


def _debug_http_shape(event: dict[str, Any], is_http_event: bool) -> None:
    if not DEBUG_HTTP_EVENT:
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


def _frontend_api_v2_doc() -> dict[str, Any]:
    return {
        "artifact": "dtm_frontend_api_v2_doc",
        "version": "2.0.0",
        "default_root_doc_version": "v2",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/v2/frontend",
                "description": "Основной endpoint для фронтенда (payload v2).",
            },
            {
                "method": "GET",
                "path": "/api/v2/frontend/doc",
                "description": "HTML-страница с документацией по контракту v2.",
            },
            {
                "method": "GET",
                "path": "/api/v2/frontend/doc?format=json",
                "description": "JSON-представление документации по контракту v2.",
            },
        ],
        "query": {
            "statuses": {
                "type": "string",
                "default": "work,pre_done",
                "description": "Список статусов через запятую.",
                "example": "work,pre_done,wait",
            },
            "designer": {
                "type": "string",
                "default": "",
                "description": "Фильтр по имени дизайнера (без учета регистра).",
                "example": "Муратов Эдуард",
            },
            "limit": {
                "type": "int",
                "default": 200,
                "range": "1..1000",
                "description": "Максимальное количество задач в ответе.",
            },
            "include_people": {
                "type": "bool",
                "default": True,
                "accepted_values": ["1", "0", "true", "false", "yes", "no"],
                "description": "Добавлять блок entities.people в ответ.",
            },
        },
        "top_level": ["meta", "filters", "summary", "entities", "tasks"],
        "field_status": {
            "meta": "implemented",
            "filters": "implemented",
            "summary": "implemented",
            "entities": "implemented",
            "tasks": "implemented",
            "tasks[].hash": "reserved",
            "tasks[].revision": "reserved",
            "tasks[].links.sheetRowUrl": "reserved",
            "entities.tags[]": "reserved",
        },
        "response_fields": {
            "meta": {
                "artifact": "string (dtm_frontend_api_v2)",
                "contractVersion": "string (2.x.x)",
                "generatedAt": "ISO-8601 UTC datetime",
                "syncedAt": "ISO-8601 UTC datetime",
                "source": {
                    "env": "string (dev|test|prod)",
                    "sourceId": "string",
                    "sheetName": "string|null",
                    "sheetUrl": "string|null",
                },
                "hash": "sha256 payload hash",
                "features": {
                    "taskHash": "bool",
                    "taskRevision": "bool",
                    "entities": "bool",
                },
                "paging": {"limit": "int", "nextCursor": "string|null"},
            },
            "filters": {
                "statuses": "string[]",
                "designer": "string",
                "limit": "int",
                "includePeople": "bool",
            },
            "summary": {
                "tasksReturned": "int",
                "peopleReturned": "int",
                "groupsReturned": "int",
            },
            "entities": {
                "people[]": {
                    "id": "string",
                    "name": "string",
                    "position": "string|null",
                    "links.self": "string",
                },
                "groups[]": {
                    "id": "string",
                    "name": "string",
                    "links.self": "string",
                },
                "tags[]": "string[]",
                "enums.status": "map<string,string>",
                "enums.statusGroups": "map<string,string[]>",
            },
            "tasks[]": {
                "id": "string",
                "title": "string",
                "ownerId": "string|null",
                "groupId": "string|null",
                "status": "string",
                "date.start": "YYYY-MM-DD|null",
                "date.end": "YYYY-MM-DD|null",
                "date.nextDue": "YYYY-MM-DD|null",
                "tags": "string[]",
                "hash": "string|null (reserved)",
                "revision": "string|int|null (reserved)",
                "links.sheetRowUrl": "string|null",
                "links.self": "string",
            },
        },
        "task_fields": [
            "id",
            "title",
            "ownerId",
            "groupId",
            "status",
            "date",
            "tags",
            "hash",
            "revision",
            "links",
        ],
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


def _frontend_api_v2_doc_html() -> str:
    return """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>DTM Frontend API v2</title>
  <style>
    body { margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f6f8fb; color: #17212b; }
    .wrap { max-width: 1080px; margin: 0 auto; padding: 24px; }
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
      <h1>DTM Frontend API v2</h1>
      <p>Контракт: <code>2.0.0</code></p>
      <p>Структура ответа: <code>meta + filters + summary + entities + tasks</code>.</p>
    </div>
    <div class="card">
      <h2>Endpoints</h2>
      <table>
        <thead><tr><th>Method</th><th>Path</th><th>Описание</th></tr></thead>
        <tbody>
          <tr><td>GET</td><td><code>/api/v2/frontend</code></td><td>Основной endpoint для фронтенда (контракт v2).</td></tr>
          <tr><td>GET</td><td><code>/api/v2/frontend/doc</code></td><td>HTML-страница с документацией.</td></tr>
          <tr><td>GET</td><td><code>/api/v2/frontend/doc?format=json</code></td><td>JSON-представление документации.</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>Параметры запроса</h2>
      <table>
        <thead><tr><th>Параметр</th><th>Тип</th><th>Default</th><th>Описание</th></tr></thead>
        <tbody>
          <tr><td><code>statuses</code></td><td>string</td><td><code>work,pre_done</code></td><td>Список статусов через запятую, например <code>work,pre_done,wait</code>.</td></tr>
          <tr><td><code>designer</code></td><td>string</td><td><code></code></td><td>Фильтр по имени дизайнера (без учета регистра).</td></tr>
          <tr><td><code>limit</code></td><td>int</td><td><code>200</code></td><td>Лимит задач в ответе, диапазон <code>1..1000</code>.</td></tr>
          <tr><td><code>include_people</code></td><td>bool</td><td><code>true</code></td><td>Включать/исключать блок <code>entities.people</code>.</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>Поля ответа</h2>
      <table>
        <thead><tr><th>Поле</th><th>Тип</th><th>Статус</th><th>Описание</th></tr></thead>
        <tbody>
          <tr><td><code>meta</code></td><td>object</td><td>implemented</td><td>Метаданные ответа: версия контракта, время генерации, hash, source и paging.</td></tr>
          <tr><td><code>meta.artifact</code></td><td>string</td><td>implemented</td><td>Идентификатор артефакта: <code>dtm_frontend_api_v2</code>.</td></tr>
          <tr><td><code>meta.contractVersion</code></td><td>string</td><td>implemented</td><td>Версия контракта API v2.</td></tr>
          <tr><td><code>meta.generatedAt</code></td><td>datetime</td><td>implemented</td><td>UTC время генерации payload.</td></tr>
          <tr><td><code>meta.syncedAt</code></td><td>datetime</td><td>implemented</td><td>UTC время последней синхронизации источника.</td></tr>
          <tr><td><code>meta.source</code></td><td>object</td><td>implemented</td><td>Контур, id источника, имя и ссылка на таблицу (если доступны).</td></tr>
          <tr><td><code>meta.hash</code></td><td>string</td><td>implemented</td><td>SHA256 от стабильной сериализации payload.</td></tr>
          <tr><td><code>filters</code></td><td>object</td><td>implemented</td><td>Echo примененных параметров запроса.</td></tr>
          <tr><td><code>summary</code></td><td>object</td><td>implemented</td><td>Счетчики: задачи, люди, группы.</td></tr>
          <tr><td><code>entities.people[]</code></td><td>array</td><td>implemented</td><td>Справочник людей: <code>id</code>, <code>name</code>, <code>position</code>, <code>links.self</code>.</td></tr>
          <tr><td><code>entities.groups[]</code></td><td>array</td><td>implemented</td><td>Справочник групп/проектов: <code>id</code>, <code>name</code>, <code>links.self</code>.</td></tr>
          <tr><td><code>entities.tags[]</code></td><td>array</td><td>reserved</td><td>Теги в payload (зарезервировано, пока отдается пустым).</td></tr>
          <tr><td><code>entities.enums</code></td><td>object</td><td>implemented</td><td>Словари статусов и групп статусов для UI.</td></tr>
          <tr><td><code>tasks[]</code></td><td>array</td><td>implemented</td><td>Основной список задач.</td></tr>
          <tr><td><code>tasks[].id</code></td><td>string</td><td>implemented</td><td>Стабильный идентификатор задачи.</td></tr>
          <tr><td><code>tasks[].title</code></td><td>string</td><td>implemented</td><td>Название задачи.</td></tr>
          <tr><td><code>tasks[].ownerId</code></td><td>string|null</td><td>implemented</td><td>ID владельца из <code>entities.people</code>.</td></tr>
          <tr><td><code>tasks[].groupId</code></td><td>string|null</td><td>implemented</td><td>ID группы из <code>entities.groups</code>.</td></tr>
          <tr><td><code>tasks[].status</code></td><td>string</td><td>implemented</td><td>Нормализованный статус задачи.</td></tr>
          <tr><td><code>tasks[].date.start/end/nextDue</code></td><td>date|null</td><td>implemented</td><td>Ключевые даты задачи в формате <code>YYYY-MM-DD</code>.</td></tr>
          <tr><td><code>tasks[].tags</code></td><td>array</td><td>implemented</td><td>Теги задачи.</td></tr>
          <tr><td><code>tasks[].hash</code></td><td>string|null</td><td>reserved</td><td>Резерв под hash задачи для инкрементальных обновлений (сейчас <code>null</code>).</td></tr>
          <tr><td><code>tasks[].revision</code></td><td>string|int|null</td><td>reserved</td><td>Резерв под версию/ревизию задачи (сейчас <code>null</code>).</td></tr>
          <tr><td><code>tasks[].links</code></td><td>object</td><td>implemented</td><td>Ссылки на self endpoint и source row (если доступно).</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>Пример запроса</h2>
      <pre>GET /api/v2/frontend?statuses=work,pre_done&limit=100&include_people=true</pre>
    </div>
    <div class="card">
      <h2>Минимальный пример ответа</h2>
      <pre>{
  "meta": {"artifact": "dtm_frontend_api_v2", "contractVersion": "2.0.0"},
  "filters": {"statuses": ["work", "pre_done"], "designer": "", "limit": 100, "includePeople": true},
  "summary": {"tasksReturned": 0, "peopleReturned": 0, "groupsReturned": 0},
  "entities": {"people": [], "groups": [], "tags": [], "enums": {"status": {}, "statusGroups": {}}},
  "tasks": []
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
    value = re.sub(r"/{2,}", "/", value)
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

    started = time.perf_counter()
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
    duration_ms = int((time.perf_counter() - started) * 1000)
    print(
        "api_response "
        f"artifact={payload.get('artifact', '')} "
        "contractVersion=1.0.0 "
        f"generatedAt={payload.get('generated_at_utc', '')} "
        "syncedAt= "
        f"tasksReturned={payload.get('summary', {}).get('tasks_returned', 0)} "
        f"duration_ms={duration_ms}"
    )
    return _json_response(200, payload)


def _handle_frontend_api_v2_if_requested(event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
    if not is_http_event:
        return None
    path = _normalize_path(_http_path(event))
    method = _http_method(event) or "GET"
    if method == "ANY":
        method = "GET"
    if method != "GET":
        return None

    params = _query_params(event)
    doc_paths = {"/api/v2/frontend/doc"}
    data_paths = {"/api/v2/frontend"}

    if _path_matches(path, doc_paths):
        if str(params.get("format", "")).strip().lower() == "json":
            return _json_response(200, _frontend_api_v2_doc())
        return _html_response(200, _frontend_api_v2_doc_html())
    if not _path_matches(path, data_paths):
        return None

    started = time.perf_counter()
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

    payload = build_frontend_api_payload_v2(
        tasks=tasks,
        people=people,
        env_name=RUNTIME_ENV,
        source_sheet_name=SOURCE_SHEET_NAME,
        statuses=statuses,
        limit=limit,
        include_people=include_people,
        designer_filter=designer,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    print(
        "api_response "
        f"artifact={payload.get('meta', {}).get('artifact', '')} "
        f"contractVersion={payload.get('meta', {}).get('contractVersion', '')} "
        f"generatedAt={payload.get('meta', {}).get('generatedAt', '')} "
        f"syncedAt={payload.get('meta', {}).get('syncedAt', '')} "
        f"tasksReturned={payload.get('summary', {}).get('tasksReturned', 0)} "
        f"duration_ms={duration_ms}"
    )
    return _json_response(200, payload)


def _handle_api_root_if_requested(event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
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
    return _json_response(200, _frontend_api_v2_doc()) if as_json else _html_response(200, _frontend_api_v2_doc_html())


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

    root_response = _handle_api_root_if_requested(event if isinstance(event, dict) else {}, is_http_event)
    if root_response is not None:
        return root_response

    frontend_v2_response = _handle_frontend_api_v2_if_requested(event if isinstance(event, dict) else {}, is_http_event)
    if frontend_v2_response is not None:
        return frontend_v2_response

    frontend_response = _handle_frontend_api_if_requested(event if isinstance(event, dict) else {}, is_http_event)
    if frontend_response is not None:
        return frontend_response

    event_dict = event if isinstance(event, dict) else {}
    _debug_http_shape(event_dict, is_http_event)
    run_mode = _extract_run_mode(event_dict, request_payload, is_http_event)
    trigger_mode = _resolve_trigger_mode(event_dict)
    if not run_mode and trigger_mode:
        run_mode = trigger_mode
    if is_http_event and not run_mode:
        # Keep future default-version knob explicit for planned generic `/api/frontend` alias.
        _ = FRONTEND_API_DEFAULT_VERSION
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

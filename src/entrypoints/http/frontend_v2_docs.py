"""Frontend API v2 documentation payload and HTML page builders."""

from __future__ import annotations

import html
import json
from typing import Any


def frontend_api_v2_doc() -> dict[str, Any]:
    return {
        "artifact": "dtm_frontend_api_v2_doc",
        "version": "2.0.1",
        "default_root_doc_version": "v2",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/v2/frontend",
                "description": "Primary frontend endpoint (v2 payload).",
            },
            {
                "method": "GET",
                "path": "/api/v2/frontend/doc",
                "description": "HTML contract documentation page.",
            },
            {
                "method": "GET",
                "path": "/api/v2/frontend/doc?format=json",
                "description": "JSON representation of API v2 contract documentation.",
            },
        ],
        "query": {
            "statuses": {
                "type": "string",
                "default": "work,pre_done",
                "description": "Comma-separated statuses list.",
                "example": "work,pre_done,wait",
            },
            "designer": {
                "type": "string",
                "default": "",
                "description": "Designer exact-name filter (case-insensitive).",
                "example": "Designer Name",
            },
            "limit": {
                "type": "int",
                "default": 200,
                "range": "1..1000",
                "description": "Maximum number of tasks in response.",
            },
            "include_people": {
                "type": "bool",
                "default": True,
                "accepted_values": ["1", "0", "true", "false", "yes", "no"],
                "description": "Include entities.people block.",
            },
            "window_start": {
                "type": "string",
                "format": "YYYY-MM-DD",
                "default": None,
                "description": "Window start date (inclusive).",
            },
            "window_end": {
                "type": "string",
                "format": "YYYY-MM-DD",
                "default": None,
                "description": "Window end date (inclusive).",
            },
            "window_mode": {
                "type": "string",
                "default": "intersects",
                "allowed_values": ["intersects"],
                "description": "Task enters window if start or end intersects.",
            },
        },
        "examples": [
            {
                "title": "Default active queue (people included by default)",
                "request": "/api/v2/frontend",
                "notes": "Equivalent to statuses=work,pre_done and include_people=true.",
            },
            {
                "title": "Limit and explicit people include",
                "request": "/api/v2/frontend?statuses=work,pre_done&include_people=true&limit=200",
                "notes": "Typical UI request for active tasks.",
            },
            {
                "title": "Filter by designer",
                "request": "/api/v2/frontend?statuses=work,pre_done&designer=Designer%20Name",
                "notes": "Case-insensitive exact-name filter on designer.",
            },
            {
                "title": "Date window filter",
                "request": "/api/v2/frontend?statuses=work,pre_done&window_start=2026-03-01&window_end=2026-03-31&window_mode=intersects",
                "notes": "Returns tasks intersecting the specified window.",
            },
        ],
        "top_level": ["meta", "filters", "summary", "entities", "tasks"],
        "field_status": {
            "meta": "implemented",
            "filters": "implemented",
            "summary": "implemented",
            "entities": "implemented",
            "tasks": "implemented",
            "tasks[].milestones": "implemented",
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
                "include_people": "bool",
                "window": {
                    "enabled": "bool",
                    "start": "YYYY-MM-DD|null",
                    "end": "YYYY-MM-DD|null",
                    "mode": "string(intersects)",
                },
            },
            "summary": {
                "tasksTotal": "int",
                "tasksReturned": "int",
                "peopleTotal": "int",
                "groupsTotal": "int",
                "milestonesTotal": "int",
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
                "brand": "string",
                "format_": "string",
                "customer": "string",
                "ownerId": "string|null",
                "groupId": "string|null",
                "status": "string",
                "date.start": "YYYY-MM-DD|null",
                "date.end": "YYYY-MM-DD|null",
                "date.nextDue": "YYYY-MM-DD|null",
                "tags": "string[]",
                "hash": "string|null (reserved, optional)",
                "revision": "string|int|null (reserved, optional)",
                "links.sheetRowUrl": "string|null (reserved, optional)",
                "links.self": "string",
                "milestones[]": {
                    "type": "string",
                    "planned": "YYYY-MM-DD|null",
                    "actual": "YYYY-MM-DD|null",
                    "status": "planned|done|unknown|skipped",
                },
            },
        },
        "task_fields": [
            "id",
            "title",
            "brand",
            "format_",
            "customer",
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


def frontend_api_v2_doc_html() -> str:
    doc = frontend_api_v2_doc()
    query_json = html.escape(
        json.dumps(doc.get("query", {}), ensure_ascii=False, indent=2, sort_keys=True)
    )
    response_fields_json = html.escape(
        json.dumps(doc.get("response_fields", {}), ensure_ascii=False, indent=2, sort_keys=True)
    )
    examples_json = html.escape(
        json.dumps(doc.get("examples", []), ensure_ascii=False, indent=2, sort_keys=True)
    )
    field_status_json = html.escape(
        json.dumps(doc.get("field_status", {}), ensure_ascii=False, indent=2, sort_keys=True)
    )
    html_doc = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>DTM Frontend API v2</title>
  <style>
    body { margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f6f8fb; color: #17212b; }
    .wrap { max-width: 1080px; margin: 0 auto; padding: 24px; }
    .card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,.06); margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; border-bottom: 1px solid #e5e7eb; padding: 8px; vertical-align: top; }
    code { background: #eef2f7; padding: 2px 6px; border-radius: 6px; }
    pre { margin: 0; overflow: auto; background: #fbfcff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>DTM Frontend API v2</h1>
      <p>Contract: <code>2.0.1</code></p>
    </div>
    <div class="card">
      <h2>Endpoints</h2>
      <table>
        <thead><tr><th>Method</th><th>Path</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>GET</td><td><code>/api/v2/frontend</code></td><td>Main frontend endpoint.</td></tr>
          <tr><td>GET</td><td><code>/api/v2/frontend/doc</code></td><td>HTML docs.</td></tr>
          <tr><td>GET</td><td><code>/api/v2/frontend/doc?format=json</code></td><td>JSON docs.</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>Field Status</h2>
      <pre><code>__FIELD_STATUS_JSON__</code></pre>
    </div>
    <div class="card">
      <h2>Query Parameters</h2>
      <pre><code>__QUERY_JSON__</code></pre>
    </div>
    <div class="card">
      <h2>Response Fields</h2>
      <pre><code>__RESPONSE_FIELDS_JSON__</code></pre>
    </div>
    <div class="card">
      <h2>Query Examples</h2>
      <pre><code>__EXAMPLES_JSON__</code></pre>
    </div>
  </div>
</body>
</html>
"""
    return (
        html_doc
        .replace("__FIELD_STATUS_JSON__", field_status_json)
        .replace("__QUERY_JSON__", query_json)
        .replace("__RESPONSE_FIELDS_JSON__", response_fields_json)
        .replace("__EXAMPLES_JSON__", examples_json)
    )

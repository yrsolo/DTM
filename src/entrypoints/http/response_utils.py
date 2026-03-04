"""HTTP response/path helpers extracted from index entrypoint."""

from __future__ import annotations

import json
from typing import Any, Callable


def json_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False),
    }


def error_response(
    status_code: int,
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    json_response_func: Callable[[int, dict[str, Any]], dict[str, Any]] = json_response,
) -> dict[str, Any]:
    return json_response_func(
        status_code,
        {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


def html_response(status_code: int, html: str) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "body": html,
    }


def path_matches(path: str, candidates: set[str], normalize_path: Callable[[str], str]) -> bool:
    normalized = normalize_path(path)
    if normalized in candidates:
        return True
    return any(normalized.endswith(candidate) for candidate in candidates)

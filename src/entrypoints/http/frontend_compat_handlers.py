"""Compatibility HTTP handlers for frontend API routing."""

from __future__ import annotations

from typing import Any, Callable


def handle_frontend_api_v1_discontinued_if_requested(
    event: dict[str, Any],
    is_http_event: bool,
    *,
    error_response: Callable[..., dict[str, Any]],
    normalize_path: Callable[[str], str],
    http_path: Callable[[dict[str, Any]], str],
    http_method: Callable[[dict[str, Any]], str],
    path_matches: Callable[[str, set[str]], bool],
) -> dict[str, Any] | None:
    if not is_http_event:
        return None
    path = normalize_path(http_path(event))
    method = http_method(event) or "GET"
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
    if not path_matches(path, v1_paths):
        return None

    return error_response(
        410,
        code="api_v1_discontinued",
        message="API v1 is discontinued. Use /api/v2/frontend and /api/v2/frontend/doc.",
    )


def handle_frontend_api_root_if_requested(
    event: dict[str, Any],
    is_http_event: bool,
    *,
    json_response: Callable[[int, dict[str, Any]], dict[str, Any]],
    html_response: Callable[[int, str], dict[str, Any]],
    normalize_path: Callable[[str], str],
    http_path: Callable[[dict[str, Any]], str],
    http_method: Callable[[dict[str, Any]], str],
    query_params: Callable[[dict[str, Any]], dict[str, Any]],
    frontend_api_v2_doc: Callable[[], dict[str, Any]],
    frontend_api_v2_doc_html: Callable[[], str],
) -> dict[str, Any] | None:
    if not is_http_event:
        return None
    method = http_method(event) or "GET"
    if method == "ANY":
        method = "GET"
    if method != "GET":
        return None
    path = normalize_path(http_path(event))
    if path not in {"/"}:
        return None
    params = query_params(event)
    as_json = str(params.get("format", "")).strip().lower() == "json"
    return (
        json_response(200, frontend_api_v2_doc())
        if as_json
        else html_response(200, frontend_api_v2_doc_html())
    )

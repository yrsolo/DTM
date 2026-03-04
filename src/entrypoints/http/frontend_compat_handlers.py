"""Compatibility HTTP handlers for frontend API routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class FrontendRootHandlerContext:
    json_response: Callable[[int, dict[str, Any]], dict[str, Any]]
    html_response: Callable[[int, str], dict[str, Any]]
    normalize_path: Callable[[str], str]
    http_path: Callable[[dict[str, Any]], str]
    http_method: Callable[[dict[str, Any]], str]
    query_params: Callable[[dict[str, Any]], dict[str, Any]]
    frontend_api_v2_doc: Callable[[], dict[str, Any]]
    frontend_api_v2_doc_html: Callable[[], str]


class FrontendRootHandler:
    """Object HTTP handler for API root/doc landing route."""

    def __init__(self, ctx: FrontendRootHandlerContext) -> None:
        self._ctx = ctx

    def handle(self, event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
        return handle_frontend_api_root_if_requested(event, is_http_event, self._ctx)


def handle_frontend_api_root_if_requested(
    event: dict[str, Any],
    is_http_event: bool,
    ctx: FrontendRootHandlerContext,
) -> dict[str, Any] | None:
    json_response = ctx.json_response
    html_response = ctx.html_response
    normalize_path = ctx.normalize_path
    http_path = ctx.http_path
    http_method = ctx.http_method
    query_params = ctx.query_params
    frontend_api_v2_doc = ctx.frontend_api_v2_doc
    frontend_api_v2_doc_html = ctx.frontend_api_v2_doc_html
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

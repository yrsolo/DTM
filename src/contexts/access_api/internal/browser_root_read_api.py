"""Compatibility HTTP handlers for frontend API routing."""

from __future__ import annotations

from src.platform.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.frontend_v2_docs import frontend_api_v2_doc, frontend_api_v2_doc_html
from src.entrypoints.http.response_utils import html_response, json_response


class BrowserRootReadApi:
    """Browser root/doc read endpoint for the access API context."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        _ = self._ctx
        if not req.is_http_event:
            return None
        method = str(req.method or "GET").strip().upper()
        if method == "ANY":
            method = "GET"
        if method != "GET":
            return None
        path = normalize_path(req.path)
        if path not in {"/"}:
            return None
        as_json = str(req.query.get("format", "")).strip().lower() == "json"
        return json_response(200, frontend_api_v2_doc()) if as_json else html_response(200, frontend_api_v2_doc_html())

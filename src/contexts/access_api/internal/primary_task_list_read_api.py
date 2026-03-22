"""Thin HTTP adapter for the primary browser task-list read."""

from __future__ import annotations

from src.contexts.access_api.application.primary_task_list_read_service import (
    PrimaryTaskListReadService,
)
from src.contexts.snapshot.module import get_query_api as _get_snapshot_query_api
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.frontend_v2_docs import frontend_api_v2_doc, frontend_api_v2_doc_html
from src.entrypoints.http.response_utils import html_response, json_response
from src.platform.context import AppContext


def get_snapshot_query_api(ctx):
    return _get_snapshot_query_api(ctx)


def get_prep_snapshot(ctx):
    return get_snapshot_query_api(ctx).get_prep_snapshot()


def get_response_cache_store(ctx):
    return get_snapshot_query_api(ctx).get_response_cache_store()


def query_frontend_v2(ctx, query):
    return get_snapshot_query_api(ctx).frontend_v2(query)


def _path_matches(path: str, candidates: set[str]) -> bool:
    normalized = normalize_path(path)
    if normalized in candidates:
        return True
    return any(normalized.endswith(candidate) for candidate in candidates)


class PrimaryTaskListReadApi:
    """HTTP adapter for the primary task-list read endpoint."""

    def __init__(self, ctx: AppContext) -> None:
        self._service = PrimaryTaskListReadService(
            ctx,
            snapshot_query_api_getter=get_snapshot_query_api,
            prep_snapshot_getter=get_prep_snapshot,
            response_cache_store_getter=get_response_cache_store,
            frontend_query_executor=query_frontend_v2,
        )

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        method = str(req.method or "GET").strip().upper()
        if method == "ANY":
            method = "GET"
        if method != "GET":
            return None

        path = normalize_path(req.path)
        params = dict(req.query)
        doc_paths = {
            "/api/v2/frontend/doc",
            "/api/v1",
            "/api/v1/frontend/doc",
            "/api/v1/read-model/doc",
        }
        data_paths = {
            "/api/v2/frontend",
            "/api/v1/frontend",
            "/api/v1/read-model",
        }

        if _path_matches(path, doc_paths):
            if str(params.get("format", "")).strip().lower() == "json":
                return json_response(200, frontend_api_v2_doc())
            return html_response(200, frontend_api_v2_doc_html())
        if not _path_matches(path, data_paths):
            return None

        return self._service.execute(req)

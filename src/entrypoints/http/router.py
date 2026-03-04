"""HTTP routing scaffold for index entrypoint delegation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.entrypoints.http.frontend_compat_handlers import handle_frontend_api_root_if_requested
from src.entrypoints.http.frontend_v2_handler import handle_frontend_api_v2_if_requested

HttpHandler = Callable[[dict[str, Any], bool], dict[str, Any] | None]


def dispatch_http(
    event: dict[str, Any],
    is_http_event: bool,
    handlers: tuple[HttpHandler, ...],
) -> dict[str, Any] | None:
    """Run handlers in order and return first non-empty HTTP response."""

    for handler in handlers:
        response = handler(event, is_http_event)
        if response is not None:
            return response
    return None


@dataclass(frozen=True)
class HttpRouterContext:
    json_response: Callable[[int, dict[str, Any]], dict[str, Any]]
    html_response: Callable[[int, str], dict[str, Any]]
    error_response: Callable[..., dict[str, Any]]
    normalize_path: Callable[[str], str]
    http_path: Callable[[dict[str, Any]], str]
    http_method: Callable[[dict[str, Any]], str]
    query_params: Callable[[dict[str, Any]], dict[str, Any]]
    path_matches: Callable[[str, set[str], Callable[[str], str]], bool]
    parse_statuses: Callable[[str], list[str]]
    parse_limit: Callable[[str, int], int]
    parse_bool: Callable[[str | None, bool], bool]
    parse_window_query: Callable[[dict[str, Any]], tuple[dict[str, Any], dict[str, Any] | None]]
    ydb_endpoint: str
    ydb_database: str
    ydb_sa_json_credentials: str | None
    ydb_sa_key_file: str | None
    app_runtime_env: str
    app_source_sheet_name: str
    frontend_api_v2_doc: Callable[[], dict[str, Any]]
    frontend_api_v2_doc_html: Callable[[], str]
    frontend_readmodel_repo_cls: Any


class HttpRouter:
    """Object router for API root + frontend v2 dispatch."""

    def __init__(self, ctx: HttpRouterContext) -> None:
        self._ctx = ctx

    def dispatch(self, event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
        for handler in (self._handle_api_root, self._handle_api_v2):
            response = handler(event, is_http_event)
            if response is not None:
                return response
        return None

    def _handle_api_root(self, event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
        ctx = self._ctx
        return handle_frontend_api_root_if_requested(
            event,
            is_http_event,
            json_response=ctx.json_response,
            html_response=ctx.html_response,
            normalize_path=ctx.normalize_path,
            http_path=ctx.http_path,
            http_method=ctx.http_method,
            query_params=ctx.query_params,
            frontend_api_v2_doc=ctx.frontend_api_v2_doc,
            frontend_api_v2_doc_html=ctx.frontend_api_v2_doc_html,
        )

    def _handle_api_v2(self, event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
        ctx = self._ctx
        return handle_frontend_api_v2_if_requested(
            event,
            is_http_event,
            json_response=ctx.json_response,
            html_response=ctx.html_response,
            error_response=ctx.error_response,
            normalize_path=ctx.normalize_path,
            http_path=ctx.http_path,
            http_method=ctx.http_method,
            query_params=ctx.query_params,
            path_matches=lambda path, candidates: ctx.path_matches(path, candidates, ctx.normalize_path),
            parse_statuses=ctx.parse_statuses,
            parse_limit=ctx.parse_limit,
            parse_bool=ctx.parse_bool,
            parse_window_query=ctx.parse_window_query,
            ydb_endpoint=ctx.ydb_endpoint,
            ydb_database=ctx.ydb_database,
            ydb_sa_json_credentials=ctx.ydb_sa_json_credentials,
            ydb_sa_key_file=ctx.ydb_sa_key_file,
            app_runtime_env=ctx.app_runtime_env,
            app_source_sheet_name=ctx.app_source_sheet_name,
            frontend_api_v2_doc=ctx.frontend_api_v2_doc,
            frontend_api_v2_doc_html=ctx.frontend_api_v2_doc_html,
            frontend_readmodel_repo_cls=ctx.frontend_readmodel_repo_cls,
        )

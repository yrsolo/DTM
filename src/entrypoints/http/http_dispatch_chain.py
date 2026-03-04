"""Build HTTP dispatch handler chain for index entrypoint."""

from __future__ import annotations

from typing import Any, Callable

from src.entrypoints.http.frontend_compat_handlers import handle_frontend_api_root_if_requested
from src.entrypoints.http.frontend_v2_handler import handle_frontend_api_v2_if_requested


def build_http_dispatch_handlers(
    *,
    json_response: Callable[[int, dict[str, Any]], dict[str, Any]],
    html_response: Callable[[int, str], dict[str, Any]],
    error_response: Callable[..., dict[str, Any]],
    normalize_path: Callable[[str], str],
    http_path: Callable[[dict[str, Any]], str],
    http_method: Callable[[dict[str, Any]], str],
    query_params: Callable[[dict[str, Any]], dict[str, Any]],
    path_matches: Callable[[str, set[str], Callable[[str], str]], bool],
    parse_statuses: Callable[[str], list[str]],
    parse_limit: Callable[[str, int], int],
    parse_bool: Callable[[str | None, bool], bool],
    parse_window_query: Callable[[dict[str, Any]], tuple[dict[str, Any], dict[str, Any] | None]],
    app_readmodel_source: str,
    ydb_endpoint: str,
    ydb_database: str,
    ydb_sa_json_credentials: str | None,
    ydb_sa_key_file: str | None,
    app_runtime_env: str,
    app_source_sheet_name: str,
    key_json: str,
    sheet_info: dict[str, str],
    app_cfg: Any,
    frontend_api_v2_doc: Callable[[], dict[str, Any]],
    frontend_api_v2_doc_html: Callable[[], str],
    frontend_readmodel_repo_cls: Any,
    build_planner_dependencies: Callable[..., Any],
    load_frontend_tasks: Callable[[Any, list[str]], list[Any]],
    build_frontend_api_payload_v2: Callable[..., dict[str, Any]],
) -> tuple[
    Callable[[dict[str, Any], bool], dict[str, Any] | None],
    Callable[[dict[str, Any], bool], dict[str, Any] | None],
]:
    def _handle_api_root(event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
        return handle_frontend_api_root_if_requested(
            event,
            is_http_event,
            json_response=json_response,
            html_response=html_response,
            normalize_path=normalize_path,
            http_path=http_path,
            http_method=http_method,
            query_params=query_params,
            frontend_api_v2_doc=frontend_api_v2_doc,
            frontend_api_v2_doc_html=frontend_api_v2_doc_html,
        )

    def _handle_api_v2(event: dict[str, Any], is_http_event: bool) -> dict[str, Any] | None:
        return handle_frontend_api_v2_if_requested(
            event,
            is_http_event,
            json_response=json_response,
            html_response=html_response,
            error_response=error_response,
            normalize_path=normalize_path,
            http_path=http_path,
            http_method=http_method,
            query_params=query_params,
            path_matches=lambda path, candidates: path_matches(path, candidates, normalize_path),
            parse_statuses=parse_statuses,
            parse_limit=parse_limit,
            parse_bool=parse_bool,
            parse_window_query=parse_window_query,
            app_readmodel_source=app_readmodel_source,
            ydb_endpoint=ydb_endpoint,
            ydb_database=ydb_database,
            ydb_sa_json_credentials=ydb_sa_json_credentials,
            ydb_sa_key_file=ydb_sa_key_file,
            app_runtime_env=app_runtime_env,
            app_source_sheet_name=app_source_sheet_name,
            key_json=key_json,
            sheet_info=sheet_info,
            app_cfg=app_cfg,
            frontend_api_v2_doc=frontend_api_v2_doc,
            frontend_api_v2_doc_html=frontend_api_v2_doc_html,
            frontend_readmodel_repo_cls=frontend_readmodel_repo_cls,
            build_planner_dependencies=build_planner_dependencies,
            load_frontend_tasks=load_frontend_tasks,
            build_frontend_api_payload_v2=build_frontend_api_payload_v2,
        )

    return (_handle_api_root, _handle_api_v2)

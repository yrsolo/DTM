"""Frontend API v2 HTTP handler extracted from index entrypoint."""

from __future__ import annotations

import time
from typing import Any, Callable

from src.services.source_policy import build_source_policy_matrix


def handle_frontend_api_v2_if_requested(
    event: dict[str, Any],
    is_http_event: bool,
    *,
    json_response: Callable[[int, dict[str, Any]], dict[str, Any]],
    html_response: Callable[[int, str], dict[str, Any]],
    error_response: Callable[..., dict[str, Any]],
    normalize_path: Callable[[str], str],
    http_path: Callable[[dict[str, Any]], str],
    http_method: Callable[[dict[str, Any]], str],
    query_params: Callable[[dict[str, Any]], dict[str, Any]],
    path_matches: Callable[[str, set[str]], bool],
    parse_statuses: Callable[[str], list[str]],
    parse_limit: Callable[[str, int], int],
    parse_bool: Callable[[str, bool], bool],
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
) -> dict[str, Any] | None:
    def _needs_readmodel_self_heal(payload: dict[str, Any]) -> bool:
        filters = payload.get("filters", {}) if isinstance(payload, dict) else {}
        entities = payload.get("entities", {}) if isinstance(payload, dict) else {}
        tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
        include_people = bool(filters.get("include_people", False))
        people_empty = isinstance(entities.get("people", []), list) and len(entities.get("people", [])) == 0
        first_task = tasks[0] if isinstance(tasks, list) and tasks else {}
        missing_business_fields = any(
            field not in first_task for field in ("brand", "format_", "customer")
        ) if isinstance(first_task, dict) else True
        return (not include_people and people_empty) or missing_business_fields

    def _self_heal_readmodel_snapshot(repo: Any, payload: dict[str, Any]) -> bool:
        try:
            from src.adapters.ydb.operational_repo import OperationalTaskRepo
            from src.services.readmodel_builder import FrontendReadmodelBuilderService

            meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
            source = meta.get("source", {}) if isinstance(meta, dict) else {}
            source_id = str(source.get("sourceId", "")).strip()
            if not source_id:
                return False
            operational_repo = OperationalTaskRepo(
                endpoint=ydb_endpoint,
                database=ydb_database,
                sa_json_credentials=ydb_sa_json_credentials,
                sa_key_file=ydb_sa_key_file,
                ensure_schema=False,
            )
            builder = FrontendReadmodelBuilderService(
                operational_repo=operational_repo,
                readmodel_repo=repo,
                source_id=source_id,
                env_name=str(source.get("env", app_runtime_env) or app_runtime_env),
                source_sheet_name=str(source.get("sheetName", app_source_sheet_name) or app_source_sheet_name),
            )
            builder.run(readmodel_id="frontend_v2:default", force_rebuild=True)
            return True
        except Exception as error:
            print(f"api_v2_readmodel_self_heal_failed error={error}")
            return False

    def _read_ydb_snapshot() -> tuple[dict[str, Any] | None, str | None]:
        try:
            repo = frontend_readmodel_repo_cls(
                endpoint=ydb_endpoint,
                database=ydb_database,
                sa_json_credentials=ydb_sa_json_credentials,
                sa_key_file=ydb_sa_key_file,
                ensure_schema=False,
            )
            row = repo.get_readmodel("frontend_v2:default")
            if row is None:
                return None, "readmodel_unavailable"
            payload = row.payload()
            if not isinstance(payload, dict):
                return None, "readmodel_payload_invalid"
            if _needs_readmodel_self_heal(payload):
                healed = _self_heal_readmodel_snapshot(repo, payload)
                if healed:
                    refreshed_row = repo.get_readmodel("frontend_v2:default")
                    if refreshed_row is not None:
                        refreshed_payload = refreshed_row.payload()
                        if isinstance(refreshed_payload, dict):
                            payload = refreshed_payload
                            row = refreshed_row
                            payload.setdefault("meta", {})
                            payload["meta"]["readmodelSelfHeal"] = "rebuilt_from_operational"
            payload.setdefault("meta", {})
            payload["meta"]["readmodelSource"] = "ydb"
            payload["meta"]["readmodelId"] = row.readmodel_id
            payload["meta"]["readmodelHash"] = row.payload_hash
            payload["meta"]["builtFromSourceHash"] = row.built_from_source_hash
            if any(
                [
                    designer,
                    limit != 200,
                    include_people is not True,
                    window_data.get("enabled", False),
                    statuses != ["work", "pre_done"],
                ]
            ):
                payload["meta"]["queryFilterApplied"] = False
                payload["meta"]["queryFilterNote"] = (
                    "YDB readmodel endpoint returns stored snapshot without per-request rebuild."
                )
            return payload, None
        except Exception as error:
            print(f"api_v2_readmodel_fallback=ydb_unavailable error={error}")
            return None, type(error).__name__

    if not is_http_event:
        return None
    path = normalize_path(http_path(event))
    method = http_method(event) or "GET"
    if method == "ANY":
        method = "GET"
    if method != "GET":
        return None

    params = query_params(event)
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

    if path_matches(path, doc_paths):
        if str(params.get("format", "")).strip().lower() == "json":
            return json_response(200, frontend_api_v2_doc())
        return html_response(200, frontend_api_v2_doc_html())
    if not path_matches(path, data_paths):
        return None

    started = time.perf_counter()
    statuses = parse_statuses(params.get("statuses", "work,pre_done"))
    designer = str(params.get("designer", "")).strip()
    limit = parse_limit(params.get("limit", "200"), 200)
    include_people = parse_bool(params.get("include_people"), True)
    window_data, window_error = parse_window_query(params)
    if window_error is not None:
        return error_response(
            400,
            code=str(window_error.get("code", "invalid_window")),
            message=str(window_error.get("message", "Invalid time window")),
            details=window_error.get("details", {}),
        )

    policy = build_source_policy_matrix(
        readmodel_source=app_readmodel_source,
        notify_source="legacy",
        render_source="legacy",
    )
    ydb_fallback = False
    if policy.api_reads_ydb():
        payload, ydb_error = _read_ydb_snapshot()
        if payload is not None:
            return json_response(200, payload)
        if ydb_error == "readmodel_unavailable":
            return error_response(
                503,
                code="readmodel_unavailable",
                message="frontend_v2 readmodel snapshot is not built yet.",
            )
        if ydb_error == "readmodel_payload_invalid":
            return error_response(
                500,
                code="readmodel_payload_invalid",
                message="Stored readmodel payload is not a valid JSON object.",
            )
        ydb_fallback = True

    try:
        dependencies = build_planner_dependencies(
            key_json,
            sheet_info,
            dry_run=True,
            mock_external=True,
            cfg=app_cfg,
        )
        if ydb_fallback:
            tasks = dependencies.task_repository.get_task_by_color_status(statuses)
        else:
            tasks = load_frontend_tasks(dependencies, statuses)
        people = []
        if include_people:
            dependencies.people_manager.get_designers()
            people = list(dependencies.people_manager.people.values())
    except Exception as error:
        print(f"api_v2_legacy_source_unavailable error={error}")
        # Emergency path: if legacy source is unavailable, try serving cached YDB snapshot.
        payload, ydb_error = _read_ydb_snapshot()
        if payload is not None:
            payload.setdefault("meta", {})
            payload["meta"]["readmodelSource"] = "ydb_emergency_fallback"
            payload["meta"]["fallbackReason"] = "legacy_source_unavailable"
            payload["meta"]["legacyErrorType"] = type(error).__name__
            return json_response(200, payload)
        return error_response(
            503,
            code="frontend_source_unavailable",
            message="Frontend data source is temporarily unavailable.",
            details={
                "source": "legacy",
                "errorType": type(error).__name__,
                "ydbFallbackErrorType": ydb_error,
            },
        )

    payload = build_frontend_api_payload_v2(
        tasks=tasks,
        people=people,
        env_name=app_runtime_env,
        source_sheet_name=app_source_sheet_name,
        statuses=statuses,
        limit=limit,
        include_people=include_people,
        designer_filter=designer,
        window_start=window_data.get("start"),
        window_end=window_data.get("end"),
        window_mode=str(window_data.get("mode", "intersects")),
    )
    if ydb_fallback:
        payload.setdefault("meta", {})
        payload["meta"]["readmodelSource"] = "legacy_fallback"
        payload["meta"]["fallbackReason"] = "ydb_unavailable"
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
    return json_response(200, payload)

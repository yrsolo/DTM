"""Frontend API v2 HTTP handler."""

from __future__ import annotations

import hashlib
import time
from datetime import date
from typing import Any

from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.frontend_query_params import (
    parse_bool,
    parse_limit,
    parse_statuses,
    parse_window_query,
)
from src.entrypoints.http.frontend_v2_docs import frontend_api_v2_doc, frontend_api_v2_doc_html
from src.entrypoints.http.response_utils import error_response, html_response, json_response


def _path_matches(path: str, candidates: set[str]) -> bool:
    normalized = normalize_path(path)
    if normalized in candidates:
        return True
    return any(normalized.endswith(candidate) for candidate in candidates)


class FrontendV2Handler:
    """HTTP handler for frontend api/doc routes."""

    def __init__(self, ctx: AppContext, *, frontend_readmodel_repo_cls: Any = FrontendReadmodelRepo) -> None:
        self._ctx = ctx
        self._frontend_readmodel_repo_cls = frontend_readmodel_repo_cls

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
        cfg = self._ctx.cfg
        deps = self._ctx.deps
        ydb_endpoint = str(deps.get("ydb_endpoint", ""))
        ydb_database = str(deps.get("ydb_database", ""))
        ydb_sa_json_credentials = deps.get("ydb_sa_json_credentials")
        ydb_sa_key_file = deps.get("ydb_sa_key_file")
        app_runtime_env = cfg.runtime.runtime.env_default
        app_source_sheet_name = str(cfg.tables.google_sheets.get("source_sheet_name_default", ""))

        def _stable_owner_id(value: str) -> str:
            seed = str(value or "").strip()
            if not seed:
                return "owner:unassigned"
            return hashlib.sha1(f"owner:{seed}".encode("utf-8")).hexdigest()[:16]

        def _needs_readmodel_self_heal(payload: dict[str, Any]) -> bool:
            filters = payload.get("filters", {}) if isinstance(payload, dict) else {}
            entities = payload.get("entities", {}) if isinstance(payload, dict) else {}
            tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
            include_people = bool(filters.get("include_people", False))
            people_empty = isinstance(entities.get("people", []), list) and len(entities.get("people", [])) == 0
            people_ids = {
                str(item.get("id", "")).strip()
                for item in entities.get("people", [])
                if isinstance(item, dict) and str(item.get("id", "")).strip()
            } if isinstance(entities.get("people", []), list) else set()
            people_ids_not_hashed = any(
                (len(pid) != 16) or any(ch not in "0123456789abcdef" for ch in pid)
                for pid in people_ids
            )
            owner_ids = [
                str(item.get("ownerId", "")).strip()
                for item in tasks
                if isinstance(item, dict) and str(item.get("ownerId", "")).strip()
            ] if isinstance(tasks, list) else []
            owner_people_mismatch = bool(owner_ids) and bool(people_ids) and any(owner not in people_ids for owner in owner_ids)
            first_task = tasks[0] if isinstance(tasks, list) and tasks else {}
            missing_business_fields = any(
                field not in first_task for field in ("brand", "format_", "customer")
            ) if isinstance(first_task, dict) else True
            missing_history_field = ("history" not in first_task) if isinstance(first_task, dict) else True
            return (
                (not include_people and people_empty)
                or missing_business_fields
                or missing_history_field
                or owner_people_mismatch
                or people_ids_not_hashed
            )

        def _enrich_payload_from_operational(payload: dict[str, Any]) -> dict[str, Any]:
            try:
                from src.adapters.ydb.operational_repo import OperationalTaskRepo

                filters = payload.get("filters", {}) if isinstance(payload, dict) else {}
                statuses = filters.get("statuses", ["work", "pre_done"])
                if not isinstance(statuses, list) or not statuses:
                    statuses = ["work", "pre_done"]
                operational_repo = OperationalTaskRepo(
                    endpoint=ydb_endpoint,
                    database=ydb_database,
                    sa_json_credentials=ydb_sa_json_credentials,
                    sa_key_file=ydb_sa_key_file,
                    ensure_schema=False,
                )
                operational_rows = operational_repo.list_tasks(statuses=[str(item).strip() for item in statuses])
                rows_by_task_id = {
                    str(row.get("task_id", "")).strip(): row
                    for row in operational_rows
                    if str(row.get("task_id", "")).strip()
                }

                tasks = payload.get("tasks", [])
                if isinstance(tasks, list):
                    for task in tasks:
                        if not isinstance(task, dict):
                            continue
                        task_id = str(task.get("id", "")).strip()
                        row = rows_by_task_id.get(task_id)
                        if row is None:
                            continue
                        for field in ("brand", "format_", "customer"):
                            if field not in task or task.get(field) in (None, ""):
                                task[field] = str(row.get(field, "")).strip()
                        if ("history" not in task) or (task.get("history") is None):
                            task["history"] = str(row.get("history", "")).strip()
                        owner_id = str(row.get("owner_id", "")).strip()
                        if owner_id:
                            task["ownerId"] = owner_id

                entities = payload.setdefault("entities", {})
                people = entities.get("people")
                include_people = bool(filters.get("include_people", False))
                if not isinstance(people, list):
                    people = []
                ids_need_migration = any(
                    (len(str(item.get("id", "")).strip()) != 16)
                    or any(ch not in "0123456789abcdef" for ch in str(item.get("id", "")).strip())
                    for item in people
                    if isinstance(item, dict)
                )
                if (not include_people) or (len(people) == 0) or ids_need_migration:
                    people_index: dict[str, dict[str, Any]] = {}
                    for task in tasks if isinstance(tasks, list) else []:
                        if not isinstance(task, dict):
                            continue
                        owner_name = str(task.get("ownerId", "")).strip()
                        if not owner_name:
                            continue
                        owner_id = _stable_owner_id(owner_name)
                        task["ownerId"] = owner_id
                        people_index[owner_id] = {
                            "id": owner_id,
                            "name": owner_name,
                            "position": "designer",
                            "links": {
                                "self": f"/api/v2/frontend/entities/people/{owner_id}",
                            },
                        }
                    def _sort_by_id(item: dict[str, Any]) -> str:
                        return str(item.get("id", ""))

                    entities["people"] = sorted(people_index.values(), key=_sort_by_id)
                    payload.setdefault("filters", {})["include_people"] = True
                    payload.setdefault("summary", {})["peopleTotal"] = len(entities["people"])
                payload.setdefault("meta", {})["readmodelSelfHeal"] = "enriched_from_operational"
                return payload
            except Exception as error:
                print(f"api_v2_readmodel_enrich_failed error={error}")
                return payload

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
                repo = self._frontend_readmodel_repo_cls(
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
                    else:
                        payload = _enrich_payload_from_operational(payload)
                payload.setdefault("meta", {})
                payload["meta"]["readmodelSource"] = "ydb"
                payload["meta"]["readmodelId"] = row.readmodel_id
                payload["meta"]["readmodelHash"] = row.payload_hash
                payload["meta"]["builtFromSourceHash"] = row.built_from_source_hash
                tasks = payload.get("tasks", [])
                if isinstance(tasks, list):
                    for task in tasks:
                        if not isinstance(task, dict):
                            continue
                        task["history"] = str(task.get("history", "") or "").strip()
                return payload, None
            except Exception as error:
                print(f"api_v2_readmodel_fallback=ydb_unavailable error={error}")
                return None, type(error).__name__

        def _coerce_iso_date(value: Any) -> date | None:
            text = str(value or "").strip()
            if not text:
                return None
            try:
                return date.fromisoformat(text[:10])
            except ValueError:
                return None

        def _window_intersects(task: dict[str, Any], *, start: date, end: date) -> bool:
            date_payload = task.get("date", {}) if isinstance(task.get("date", {}), dict) else {}
            task_start = _coerce_iso_date(date_payload.get("start"))
            task_end = _coerce_iso_date(date_payload.get("end"))
            if task_start is None and task_end is None:
                return False
            if task_start is None:
                task_start = task_end
            if task_end is None:
                task_end = task_start
            if task_start is None or task_end is None:
                return False
            return not (task_end < start or task_start > end)

        def _apply_query_filters(payload: dict[str, Any]) -> dict[str, Any]:
            tasks = payload.get("tasks", [])
            if not isinstance(tasks, list):
                return payload
            filtered_tasks = [task for task in tasks if isinstance(task, dict)]

            statuses_set = {str(item).strip().lower() for item in statuses if str(item).strip()}
            if statuses_set:
                filtered_tasks = [
                    task for task in filtered_tasks
                    if str(task.get("status", "work")).strip().lower() in statuses_set
                ]

            people = payload.get("entities", {}).get("people", [])
            if not isinstance(people, list):
                people = []
            designer_to_owner: dict[str, str] = {}
            for person in people:
                if not isinstance(person, dict):
                    continue
                person_name = str(person.get("name", "")).strip()
                person_id = str(person.get("id", "")).strip()
                if person_name and person_id:
                    designer_to_owner[person_name.casefold()] = person_id

            if designer:
                target_owner = designer_to_owner.get(designer.casefold(), designer)
                target_owner_fold = str(target_owner).strip().casefold()
                filtered_tasks = [
                    task for task in filtered_tasks
                    if str(task.get("ownerId", "")).strip().casefold() == target_owner_fold
                ]

            window_enabled = bool(window_data.get("enabled", False))
            window_start = _coerce_iso_date(window_data.get("start"))
            window_end = _coerce_iso_date(window_data.get("end"))
            if window_enabled and window_start is not None and window_end is not None:
                filtered_tasks = [
                    task for task in filtered_tasks
                    if _window_intersects(task, start=window_start, end=window_end)
                ]

            tasks_total = len(filtered_tasks)
            limited_tasks = filtered_tasks[: max(limit, 0)]
            payload["tasks"] = limited_tasks

            entities = payload.setdefault("entities", {})
            if include_people:
                owner_ids = {str(task.get("ownerId", "")).strip() for task in limited_tasks}
                entities["people"] = [
                    person for person in people
                    if isinstance(person, dict) and str(person.get("id", "")).strip() in owner_ids
                ]
            else:
                entities["people"] = []

            groups = entities.get("groups", [])
            if isinstance(groups, list):
                group_ids = {str(task.get("groupId", "")).strip() for task in limited_tasks}
                entities["groups"] = [
                    group for group in groups
                    if isinstance(group, dict) and str(group.get("id", "")).strip() in group_ids
                ]

            filters_payload = payload.setdefault("filters", {})
            filters_payload["statuses"] = [str(item).strip().lower() for item in statuses if str(item).strip()]
            filters_payload["designer"] = designer or None
            filters_payload["include_people"] = bool(include_people)
            filters_payload["limit"] = int(limit)
            filters_payload["window"] = {
                "enabled": bool(window_data.get("enabled", False)),
                "start": window_start.isoformat() if window_start is not None else None,
                "end": window_end.isoformat() if window_end is not None else None,
                "mode": str(window_data.get("mode", "intersects") or "intersects"),
            }

            summary = payload.setdefault("summary", {})
            summary["tasksTotal"] = tasks_total
            summary["tasksReturned"] = len(limited_tasks)
            summary["peopleTotal"] = len(entities.get("people", [])) if isinstance(entities.get("people", []), list) else 0
            summary["groupsTotal"] = len(entities.get("groups", [])) if isinstance(entities.get("groups", []), list) else 0
            summary["milestonesTotal"] = sum(
                len(task.get("milestones", []))
                for task in limited_tasks
                if isinstance(task.get("milestones", []), list)
            )

            payload.setdefault("meta", {})
            payload["meta"]["queryFilterApplied"] = True
            payload["meta"]["queryFilterNote"] = ""
            return payload

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

        payload, ydb_error = _read_ydb_snapshot()
        if payload is None:
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
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={
                    "source": "readmodel",
                    "errorType": ydb_error,
                },
            )
        payload = _apply_query_filters(payload)

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

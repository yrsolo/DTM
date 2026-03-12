"""Frontend API v2 HTTP handler backed by snapshot engine."""

from __future__ import annotations

import time

from src.app.context import AppContext
from src.entrypoints.http.access_context import resolve_access_context
from src.entrypoints.http.frontend_response_cache import (
    build_default_frontend_cache_query_hash,
    build_response_cache_entry,
    cached_payload_with_access,
    default_frontend_cache_key,
    is_default_frontend_cache_query,
    resolve_frontend_route_class,
    response_cache_entry_is_fresh,
)
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
from src.entrypoints_adapters.api_v2_adapter import build_frontend_query
from src.observability.bottlenecks import (
    append_response_headers,
    is_stage_metrics_enabled,
    new_stage_trace_id,
    record_api_stage,
)
from src.services.access import mask_frontend_payload
from src.services.access.masking import masking_version_for_hour
from src.snapshot_engine import build_snapshot_engine


def _path_matches(path: str, candidates: set[str]) -> bool:
    normalized = normalize_path(path)
    if normalized in candidates:
        return True
    return any(normalized.endswith(candidate) for candidate in candidates)


class FrontendV2Handler:
    """HTTP handler for frontend api/doc routes."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def _metrics_labels(self, *, mode: str, result: str) -> dict[str, str]:
        return {
            "env": str(self._ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev",
            "module": "api",
            "operation": "frontend_access",
            "result": f"{mode}_{result}",
        }

    @staticmethod
    def _access_payload(access) -> dict[str, object]:
        return {
            "mode": access.mode,
            "trustedIngress": bool(access.trusted_ingress),
            "authenticated": bool(access.authenticated),
            "contour": str(access.contour or "").strip(),
            "userRole": access.user_role,
            "userStatus": access.user_status,
            "fallbackReason": access.fallback_reason,
        }

    @staticmethod
    def _with_headers(response: HttpResponse, extra_headers: dict[str, str]) -> HttpResponse:
        return HttpResponse(
            status=response.status,
            body=response.body,
            headers=append_response_headers(response.headers, extra_headers),
        )

    def _frontend_debug_headers(
        self,
        *,
        req: HttpRequest,
        trace_id: str,
        route_class: str,
        access_mode: str,
        cache_result: str,
        handler_total_ms: float,
        inner_total_ms: float,
    ) -> dict[str, str]:
        if not is_stage_metrics_enabled(self._ctx):
            return {}
        if normalize_path(req.path) != "/api/v2/frontend":
            return {}
        if route_class != "api":
            return {}
        return {
            "X-DTM-Trace-Id": trace_id,
            "X-DTM-Frontend-Handler-Ms": f"{round(float(handler_total_ms), 3):.3f}",
            "X-DTM-Frontend-Inner-Ms": f"{round(float(inner_total_ms), 3):.3f}",
            "X-DTM-Frontend-Route": route_class,
            "X-DTM-Frontend-Access-Mode": access_mode,
            "X-DTM-Frontend-Cache-Result": cache_result,
        }

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

        query_parse_started = time.perf_counter()
        statuses = parse_statuses(params.get("statuses", "work,pre_done"))
        designer = str(params.get("designer", "")).strip()
        limit = parse_limit(params.get("limit", "200"), 200)
        include_people = parse_bool(params.get("include_people"), True)
        window_data, window_error = parse_window_query(params)
        query_parse_ms = (time.perf_counter() - query_parse_started) * 1000.0
        if window_error is not None:
            return error_response(
                400,
                code=str(window_error.get("code", "invalid_window")),
                message=str(window_error.get("message", "Invalid time window")),
                details=window_error.get("details", {}),
            )

        started = time.perf_counter()
        trace_id = new_stage_trace_id()
        stage_samples: list[tuple[str, float]] = []
        stage_samples.append(("query_parse", query_parse_ms))

        def _record_stage(stage: str, started_at: float) -> None:
            stage_samples.append((stage, (time.perf_counter() - started_at) * 1000.0))

        def _emit_stages(
            *,
            route_class: str,
            access_mode: str,
            cache_result: str,
            result: str = "success",
            debug_fields: dict[str, object] | None = None,
        ) -> None:
            for stage, duration_ms in stage_samples:
                record_api_stage(
                    self._ctx,
                    trace_id=trace_id,
                    operation="frontend_access",
                    stage=stage,
                    duration_ms=duration_ms,
                    result=result,
                    route=route_class,
                    access_mode=access_mode,
                    cache_result=cache_result,
                    debug_fields=debug_fields,
                )
            record_api_stage(
                self._ctx,
                trace_id=trace_id,
                operation="frontend_access",
                stage="handler_total",
                duration_ms=(time.perf_counter() - started) * 1000.0,
                result=result,
                route=route_class,
                access_mode=access_mode,
                cache_result=cache_result,
                debug_fields=debug_fields,
            )

        def _inner_total_ms() -> float:
            return float(sum(duration_ms for _, duration_ms in stage_samples))

        access_started = time.perf_counter()
        access = resolve_access_context(self._ctx, req)
        _record_stage("access_resolution", access_started)
        try:
            engine_started = time.perf_counter()
            snapshot_engine = build_snapshot_engine(self._ctx)
            _record_stage("snapshot_engine_build", engine_started)
            frontend_query = build_frontend_query(
                statuses=statuses,
                designer=designer,
                limit=limit,
                include_people=include_people,
                window_data=window_data,
            )
        except Exception as error:
            route_class = resolve_frontend_route_class(req, access)
            _emit_stages(
                route_class=route_class,
                access_mode=access.mode,
                cache_result="bypass",
                result="failed",
                debug_fields={
                    "path": normalize_path(req.path),
                    "statuses": list(statuses),
                    "limit": limit,
                    "includePeople": include_people,
                    "queryEligible": False,
                    "errorType": type(error).__name__,
                },
            )
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={"source": "snapshot", "errorType": type(error).__name__},
            )
        metrics = self._ctx.deps.get("metrics_client")
        cache_ttl_minutes = max(int(self._ctx.cfg.runtime.api.get("frontend_response_cache_ttl_minutes", 15) or 15), 1)
        cache_eligible = is_default_frontend_cache_query(
            statuses=statuses,
            designer=designer,
            limit=limit,
            include_people=include_people,
            window_data=window_data,
        )
        route_class = resolve_frontend_route_class(req, access)
        masking_version = masking_version_for_hour(
            str(self._ctx.cfg.runtime.api.get("auth_mask_dictionary_version", "v1") or "v1")
        )
        hour_bucket = masking_version.rsplit(":", 1)[-1] if access.masked else ""
        query_hash = build_default_frontend_cache_query_hash()
        payload: dict[str, object]
        prep_started = time.perf_counter()
        prep = snapshot_engine.get_prep_snapshot()
        _record_stage("prep_snapshot_access", prep_started)
        if prep is None:
            _emit_stages(
                route_class=route_class,
                access_mode=access.mode,
                cache_result="bypass",
                result="failed",
                debug_fields={
                    "path": normalize_path(req.path),
                    "statuses": list(statuses),
                    "limit": limit,
                    "includePeople": include_people,
                    "queryEligible": cache_eligible,
                    "errorType": "prep_snapshot_unavailable",
                },
            )
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={"source": "snapshot", "errorType": "prep_snapshot_unavailable"},
            )
        cache_store = snapshot_engine.get_response_cache_store()
        if cache_eligible and cache_store is not None:
            cache_key = default_frontend_cache_key(route_class=route_class, access_mode=access.mode)
            cache_labels = {
                "env": str(self._ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev",
                "route": route_class,
                "access_mode": access.mode,
                "result": "success",
            }
            cache_read_started = time.perf_counter()
            cached_entry = cache_store.get(cache_key)
            _record_stage("response_cache_read", cache_read_started)
            if metrics is not None:
                metrics.timing(
                    "dtm.api.response_cache.read_ms",
                    (time.perf_counter() - cache_read_started) * 1000.0,
                    labels=dict(cache_labels),
                )
            freshness_started = time.perf_counter()
            if response_cache_entry_is_fresh(
                cached_entry,
                source_hash=str(prep.raw_source_hash or ""),
                route_class=route_class,
                access_mode=access.mode,
                query_hash=query_hash,
                ttl_minutes=cache_ttl_minutes,
                hour_bucket=hour_bucket,
            ):
                _record_stage("response_cache_freshness", freshness_started)
                if metrics is not None:
                    metrics.counter("dtm.api.response_cache.hit_total", labels=dict(cache_labels))
                cached_payload = dict(cached_entry.get("payload", {}) or {})
                payload = cached_payload_with_access(cached_payload, access)
                response_started = time.perf_counter()
                http_response = json_response(200, payload)
                _record_stage("response_build", response_started)
                http_response = self._with_headers(
                    http_response,
                    self._frontend_debug_headers(
                        req=req,
                        trace_id=trace_id,
                        route_class=route_class,
                        access_mode=access.mode,
                        cache_result="hit",
                        handler_total_ms=(time.perf_counter() - started) * 1000.0,
                        inner_total_ms=_inner_total_ms(),
                    ),
                )
                _emit_stages(
                    route_class=route_class,
                    access_mode=access.mode,
                    cache_result="hit",
                    debug_fields={
                        "path": normalize_path(req.path),
                        "statuses": list(statuses),
                        "limit": limit,
                        "includePeople": include_people,
                        "queryEligible": cache_eligible,
                        "cacheKey": cache_key,
                    },
                )
                duration_ms = int((time.perf_counter() - started) * 1000)
                print(
                    "api_response "
                    f"artifact={payload.get('meta', {}).get('artifact', '')} "
                    f"contractVersion={payload.get('meta', {}).get('contractVersion', '')} "
                    f"generatedAt={payload.get('meta', {}).get('generatedAt', '')} "
                    f"syncedAt={payload.get('meta', {}).get('syncedAt', '')} "
                    f"access_mode={payload.get('meta', {}).get('access', {}).get('mode', '')} "
                    f"tasksReturned={payload.get('summary', {}).get('tasksReturned', 0)} "
                    f"duration_ms={duration_ms}"
                )
                return http_response
            _record_stage("response_cache_freshness", freshness_started)
            if metrics is not None:
                metrics.counter("dtm.api.response_cache.miss_total", labels=dict(cache_labels))

        try:
            payload_build_started = time.perf_counter()
            payload = snapshot_engine.frontend_v2(frontend_query)
            _record_stage("frontend_payload_build", payload_build_started)
        except Exception as error:
            _emit_stages(
                route_class=route_class,
                access_mode=access.mode,
                cache_result="miss" if cache_eligible and cache_store is not None else "bypass",
                result="failed",
                debug_fields={
                    "path": normalize_path(req.path),
                    "statuses": list(statuses),
                    "limit": limit,
                    "includePeople": include_people,
                    "queryEligible": cache_eligible,
                    "errorType": type(error).__name__,
                },
            )
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={"source": "snapshot", "errorType": type(error).__name__},
            )
        payload = dict(payload)
        payload["meta"] = dict(payload.get("meta", {}) or {})
        payload["meta"]["access"] = self._access_payload(access)
        masking_started = time.perf_counter()
        payload = mask_frontend_payload(
            payload,
            access,
            dictionary_version=masking_version,
            metrics_client=metrics,
            metrics_labels=self._metrics_labels(mode=access.mode, result="success"),
        )
        _record_stage("masking", masking_started)
        if cache_eligible and cache_store is not None:
            cache_labels = {
                "env": str(self._ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev",
                "route": route_class,
                "access_mode": access.mode,
                "result": "success",
            }
            cache_key = default_frontend_cache_key(route_class=route_class, access_mode=access.mode)
            cache_write_started = time.perf_counter()
            cache_store.put(
                cache_key,
                build_response_cache_entry(
                    payload=payload,
                    source_hash=str(prep.raw_source_hash or ""),
                    route_class=route_class,
                    access_mode=access.mode,
                    query_hash=query_hash,
                    hour_bucket=hour_bucket,
                ),
            )
            _record_stage("response_cache_write", cache_write_started)
            if metrics is not None:
                metrics.timing(
                    "dtm.api.response_cache.write_ms",
                    (time.perf_counter() - cache_write_started) * 1000.0,
                    labels=dict(cache_labels),
                )
                metrics.counter("dtm.api.response_cache.write_total", labels=dict(cache_labels))

        response_started = time.perf_counter()
        http_response = json_response(200, payload)
        _record_stage("response_build", response_started)
        http_response = self._with_headers(
            http_response,
            self._frontend_debug_headers(
                req=req,
                trace_id=trace_id,
                route_class=route_class,
                access_mode=access.mode,
                cache_result="miss" if cache_eligible and cache_store is not None else "bypass",
                handler_total_ms=(time.perf_counter() - started) * 1000.0,
                inner_total_ms=_inner_total_ms(),
            ),
        )
        _emit_stages(
            route_class=route_class,
            access_mode=access.mode,
            cache_result="miss" if cache_eligible and cache_store is not None else "bypass",
            debug_fields={
                "path": normalize_path(req.path),
                "statuses": list(statuses),
                "limit": limit,
                "includePeople": include_people,
                "queryEligible": cache_eligible,
                "cacheKey": default_frontend_cache_key(route_class=route_class, access_mode=access.mode)
                if cache_eligible and cache_store is not None
                else "",
            },
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        print(
            "api_response "
            f"artifact={payload.get('meta', {}).get('artifact', '')} "
            f"contractVersion={payload.get('meta', {}).get('contractVersion', '')} "
            f"generatedAt={payload.get('meta', {}).get('generatedAt', '')} "
            f"syncedAt={payload.get('meta', {}).get('syncedAt', '')} "
            f"access_mode={payload.get('meta', {}).get('access', {}).get('mode', '')} "
            f"tasksReturned={payload.get('summary', {}).get('tasksReturned', 0)} "
            f"duration_ms={duration_ms}"
        )
        return http_response

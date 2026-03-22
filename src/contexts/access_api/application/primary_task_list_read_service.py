"""Application-owned orchestration for the primary browser task-list read."""

from __future__ import annotations

import time

from src.contexts.access_api.internal.frontend_query import build_frontend_query
from src.contexts.access_api.internal.frontend_response_cache import (
    build_default_frontend_cache_query_hash,
    build_response_cache_entry,
    cached_payload_with_access,
    default_frontend_cache_key,
    is_default_frontend_cache_query,
    resolve_frontend_route_class,
    response_cache_entry_is_fresh,
)
from src.contexts.access_api.internal.masking import mask_frontend_payload, masking_version_for_hour
from src.contexts.snapshot.module import get_query_api as _get_snapshot_query_api
from src.entrypoints.http.access_context import resolve_access_context
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.frontend_query_params import (
    parse_bool,
    parse_limit,
    parse_statuses,
    parse_window_query,
)
from src.entrypoints.http.response_utils import error_response, json_response
from src.platform.context import AppContext
from src.platform.observability.bottlenecks import (
    is_api_metrics_enabled,
)

from .frontend_access_observer import FrontendAccessObserver


class PrimaryTaskListReadService:
    """Own the primary browser task-list read orchestration."""

    def __init__(
        self,
        ctx: AppContext,
        *,
        snapshot_query_api_getter=None,
        prep_snapshot_getter=None,
        response_cache_store_getter=None,
        frontend_query_executor=None,
    ) -> None:
        self._ctx = ctx
        self._snapshot_query_api_getter = snapshot_query_api_getter or (lambda inner_ctx: _get_snapshot_query_api(inner_ctx))
        self._prep_snapshot_getter = prep_snapshot_getter
        self._response_cache_store_getter = response_cache_store_getter
        self._frontend_query_executor = frontend_query_executor

    def _snapshot_query_api(self):
        return self._snapshot_query_api_getter(self._ctx)

    def _prep_snapshot(self):
        if self._prep_snapshot_getter is not None:
            return self._prep_snapshot_getter(self._ctx)
        return self._snapshot_query_api().get_prep_snapshot()

    def _response_cache_store(self):
        if self._response_cache_store_getter is not None:
            return self._response_cache_store_getter(self._ctx)
        return self._snapshot_query_api().get_response_cache_store()

    def _execute_frontend_query(self, frontend_query):
        if self._frontend_query_executor is not None:
            return self._frontend_query_executor(self._ctx, frontend_query)
        return self._snapshot_query_api().frontend_v2(frontend_query)

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

    def execute(self, req: HttpRequest) -> HttpResponse:
        params = dict(req.query)
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

        observer = FrontendAccessObserver(self._ctx, req)
        observer.add_sample("query_parse", query_parse_ms)

        access_started = time.perf_counter()
        access = resolve_access_context(self._ctx, req)
        observer.stage("access_resolution", access_started)
        try:
            query_api_started = time.perf_counter()
            snapshot_query = self._snapshot_query_api()
            observer.stage("snapshot_query_api", query_api_started)
            frontend_query = build_frontend_query(
                statuses=statuses,
                designer=designer,
                limit=limit,
                include_people=include_people,
                window_data=window_data,
            )
        except Exception as error:
            route_class = resolve_frontend_route_class(req, access)
            observer.emit(
                route_class=route_class,
                access_mode=access.mode,
                cache_result="bypass",
                result="failed",
                debug_fields={"path": req.path, "errorType": type(error).__name__},
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

        prep_started = time.perf_counter()
        try:
            prep = self._prep_snapshot()
            observer.stage("prep_snapshot_access", prep_started)
            cache_store = self._response_cache_store()
        except Exception as error:
            observer.emit(
                route_class=route_class,
                access_mode=access.mode,
                cache_result="bypass",
                result="failed",
                debug_fields={"path": req.path, "errorType": type(error).__name__},
            )
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={"source": "snapshot", "errorType": type(error).__name__},
            )
        if prep is None:
            observer.emit(
                route_class=route_class,
                access_mode=access.mode,
                cache_result="bypass",
                result="failed",
                debug_fields={"path": req.path, "errorType": "prep_snapshot_unavailable"},
            )
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={"source": "snapshot", "errorType": "prep_snapshot_unavailable"},
            )

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
            observer.stage("response_cache_read", cache_read_started)
            if metrics is not None and is_api_metrics_enabled(self._ctx):
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
                observer.stage("response_cache_freshness", freshness_started)
                if metrics is not None and is_api_metrics_enabled(self._ctx):
                    metrics.counter("dtm.api.response_cache.hit_total", labels=dict(cache_labels))
                payload = cached_payload_with_access(dict(cached_entry.get("payload", {}) or {}), access)
                response_started = time.perf_counter()
                http_response = json_response(200, payload)
                observer.stage("response_build", response_started)
                handler_total_ms = observer.emit(
                    route_class=route_class,
                    access_mode=access.mode,
                    cache_result="hit",
                    debug_fields={"path": req.path, "cacheKey": cache_key},
                )
                return FrontendAccessObserver.with_headers(
                    http_response,
                    observer.debug_headers(
                        req=req,
                        route_class=route_class,
                        access_mode=access.mode,
                        cache_result="hit",
                        handler_total_ms=handler_total_ms,
                    ),
                )
            observer.stage("response_cache_freshness", freshness_started)
            if metrics is not None and is_api_metrics_enabled(self._ctx):
                metrics.counter("dtm.api.response_cache.miss_total", labels=dict(cache_labels))

        try:
            payload_build_started = time.perf_counter()
            payload = dict(self._execute_frontend_query(frontend_query))
            observer.stage("frontend_payload_build", payload_build_started)
        except Exception as error:
            observer.emit(
                route_class=route_class,
                access_mode=access.mode,
                cache_result="miss" if cache_eligible and cache_store is not None else "bypass",
                result="failed",
                debug_fields={"path": req.path, "errorType": type(error).__name__},
            )
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={"source": "snapshot", "errorType": type(error).__name__},
            )

        payload["meta"] = dict(payload.get("meta", {}) or {})
        payload["meta"]["access"] = self._access_payload(access)
        masking_started = time.perf_counter()
        payload = mask_frontend_payload(
            payload,
            access,
            dictionary_version=masking_version,
            metrics_client=metrics if is_api_metrics_enabled(self._ctx) else None,
            metrics_labels=self._metrics_labels(mode=access.mode, result="success"),
        )
        observer.stage("masking", masking_started)

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
            observer.stage("response_cache_write", cache_write_started)
            if metrics is not None and is_api_metrics_enabled(self._ctx):
                metrics.timing(
                    "dtm.api.response_cache.write_ms",
                    (time.perf_counter() - cache_write_started) * 1000.0,
                    labels=dict(cache_labels),
                )
                metrics.counter("dtm.api.response_cache.write_total", labels=dict(cache_labels))

        response_started = time.perf_counter()
        http_response = json_response(200, payload)
        observer.stage("response_build", response_started)
        cache_result = "miss" if cache_eligible and cache_store is not None else "bypass"
        handler_total_ms = observer.emit(
            route_class=route_class,
            access_mode=access.mode,
            cache_result=cache_result,
            debug_fields={"path": req.path},
        )
        return FrontendAccessObserver.with_headers(
            http_response,
            observer.debug_headers(
                req=req,
                route_class=route_class,
                access_mode=access.mode,
                cache_result=cache_result,
                handler_total_ms=handler_total_ms,
            ),
        )

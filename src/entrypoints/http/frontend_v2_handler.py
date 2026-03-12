"""Frontend API v2 HTTP handler backed by snapshot engine."""

from __future__ import annotations

import time

from src.app.context import AppContext
from src.entrypoints.http.access_context import resolve_access_context
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
from src.services.access import mask_frontend_payload
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

        started = time.perf_counter()
        try:
            snapshot_engine = build_snapshot_engine(self._ctx)
            payload = snapshot_engine.frontend_v2(
                build_frontend_query(
                    statuses=statuses,
                    designer=designer,
                    limit=limit,
                    include_people=include_people,
                    window_data=window_data,
                )
            )
        except Exception as error:
            return error_response(
                503,
                code="frontend_source_unavailable",
                message="Frontend data source is temporarily unavailable.",
                details={"source": "snapshot", "errorType": type(error).__name__},
            )
        access = resolve_access_context(self._ctx, req)
        metrics = self._ctx.deps.get("metrics_client")
        payload = dict(payload)
        payload["meta"] = dict(payload.get("meta", {}) or {})
        payload["meta"]["access"] = {
            "mode": access.mode,
            "trustedIngress": bool(access.trusted_ingress),
            "authenticated": bool(access.authenticated),
            "contour": str(access.contour or "").strip(),
            "userRole": access.user_role,
            "userStatus": access.user_status,
            "fallbackReason": access.fallback_reason,
        }
        payload = mask_frontend_payload(
            payload,
            access,
            dictionary_version=str(self._ctx.cfg.runtime.api.get("auth_mask_dictionary_version", "v1") or "v1"),
            metrics_client=metrics,
            metrics_labels=self._metrics_labels(mode=access.mode, result="success"),
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
        return json_response(200, payload)

"""Application-owned orchestration for the operational info read path."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable

from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.event_parser import normalize_path
from src.platform.observability.bottlenecks import (
    RECENT_API_STAGE_EVENTS,
    RECENT_DIRECT_API_OUTER_TRACES,
    is_api_metrics_enabled,
    is_debug_metrics_enabled,
    is_stage_metrics_enabled,
    resolve_bottleneck_metrics_level,
)
from src.platform.observability.buffered_metrics import metrics_sink_name, remote_metrics_enabled
from src.platform.runtime.command_runtime import get_command_runtime
from src.platform.runtime.worker.model import JobStatusRecord


@dataclass(frozen=True, slots=True)
class OperationalInfoRequestMode:
    detail_mode: bool
    as_json: bool


class OperationalInfoReadService:
    """Own operational info payload assembly while the adapter stays thin."""

    def __init__(
        self,
        ctx,
        *,
        resolve_ui_base_path: Callable[[HttpRequest], str],
        join_ui_path: Callable[[str, str], str],
        resolve_root_prefix: Callable[[str], str],
        storage_stats_loader: Callable[[str, str], dict[str, Any]],
        queue_live_stats_loader: Callable[..., Any],
        latest_jobs_payload_builder: Callable[[Any], dict[str, Any]],
        recent_jobs_payload_builder: Callable[[Any], dict[str, Any]],
        build_payload_loader: Callable[[str], dict[str, Any]],
        attachments_harness_builder: Callable[[HttpRequest, Any | None], dict[str, Any]],
        metrics_labels_builder: Callable[..., dict[str, str]],
        prep_snapshot_getter: Callable[[], Any | None],
        raw_snapshot_getter: Callable[[], Any | None],
        render_debug_payload_builder: Callable[[JobStatusRecord | None], dict[str, Any]],
    ) -> None:
        self._ctx = ctx
        self._resolve_ui_base_path = resolve_ui_base_path
        self._join_ui_path = join_ui_path
        self._resolve_root_prefix = resolve_root_prefix
        self._storage_stats_loader = storage_stats_loader
        self._queue_live_stats_loader = queue_live_stats_loader
        self._latest_jobs_payload_builder = latest_jobs_payload_builder
        self._recent_jobs_payload_builder = recent_jobs_payload_builder
        self._build_payload_loader = build_payload_loader
        self._attachments_harness_builder = attachments_harness_builder
        self._metrics_labels_builder = metrics_labels_builder
        self._get_prep_snapshot = prep_snapshot_getter
        self._get_raw_snapshot = raw_snapshot_getter
        self._render_debug_payload_builder = render_debug_payload_builder

    def resolve_request_mode(self, req: HttpRequest) -> OperationalInfoRequestMode | None:
        if not req.is_http_event:
            return None
        method = str(req.method or "GET").strip().upper()
        if method == "ANY":
            method = "GET"
        if method != "GET":
            return None
        path = normalize_path(req.path)
        detail_mode = (
            path in {"/info/detail", "/api/v2/info/detail"}
            or str(req.query.get("view", "")).strip().lower() == "detail"
        )
        if path not in {"/info", "/api/v2/info", "/info/detail", "/api/v2/info/detail"}:
            return None
        as_json = (
            str(req.query.get("format", "")).strip().lower() == "json"
            or path in {"/api/v2/info", "/api/v2/info/detail"}
        )
        return OperationalInfoRequestMode(detail_mode=detail_mode, as_json=as_json)

    def build_payload(self, req: HttpRequest, *, detail_mode: bool) -> dict[str, Any]:
        env_name = str(self._ctx.cfg.runtime.runtime.env_default).strip().lower() or "dev"
        metrics = self._ctx.deps.get("metrics_client")
        summary_started = perf_counter()
        payload = self._summary_payload(req)
        if metrics is not None and is_api_metrics_enabled(self._ctx):
            metrics.timing(
                "dtm.info.summary.ms",
                (perf_counter() - summary_started) * 1000.0,
                self._metrics_labels_builder(env_name=env_name, view="summary"),
            )
        if detail_mode:
            detail_started = perf_counter()
            payload = self._detail_payload(req, payload)
            if metrics is not None and is_api_metrics_enabled(self._ctx):
                metrics.timing(
                    "dtm.info.detail.ms",
                    (perf_counter() - detail_started) * 1000.0,
                    self._metrics_labels_builder(env_name=env_name, view="detail"),
                )
        return payload

    def _queue_live_payload(self, queue_url: str) -> dict[str, Any]:
        if not queue_url:
            return {"error": "queue_url_missing"}
        try:
            stats = self._queue_live_stats_loader(
                queue_url=queue_url,
                endpoint_url=str(self._ctx.cfg.runtime.queue.endpoint_url or "").strip() or None,
                aws_access_key_id=self._ctx.deps.get("aws_access_key_id"),
                aws_secret_access_key=self._ctx.deps.get("aws_secret_access_key"),
            )
        except Exception as exc:
            return {"queue_name": queue_url.rstrip("/").rsplit("/", 1)[-1], "error": str(exc)}
        return stats.to_dict()

    def _summary_payload(self, req: HttpRequest) -> dict[str, Any]:
        env_name = str(self._ctx.cfg.runtime.runtime.env_default).strip().lower() or "dev"
        snap_cfg = self._ctx.cfg.runtime.snapshot_engine
        queue_cfg = self._ctx.cfg.runtime.queue
        telegram_cfg = self._ctx.cfg.runtime.telegram
        raw_key = str(snap_cfg.prefix_raw).replace("{env}", env_name)
        root_prefix = self._resolve_root_prefix(raw_key)
        queue_url = str(queue_cfg.prod_queue_url if env_name == "prod" else queue_cfg.test_queue_url).strip()
        queue_name = queue_url.rstrip("/").rsplit("/", 1)[-1] if queue_url else ""
        webhook_path = str(telegram_cfg.webhook_path or "/telegram").strip() or "/telegram"
        api_domain = str(
            self._ctx.cfg.runtime.web.get("api_domain_prod" if env_name == "prod" else "api_domain_test", "")
        ).strip()
        webhook_url = f"https://{api_domain}{webhook_path}" if api_domain else webhook_path
        ui_base_path = self._resolve_ui_base_path(req)
        prometheus_cfg = getattr(self._ctx.cfg.runtime, "prometheus", None)
        grafana_cfg = getattr(self._ctx.cfg.runtime, "grafana", None)
        function_name = str(
            self._ctx.cfg.deploy.yandex_cloud.function_name_prod
            if env_name == "prod"
            else self._ctx.cfg.deploy.yandex_cloud.function_name_test
        ).strip()
        telemetry_payload = {
            "metricsEnabled": self._ctx.deps.get("metrics_client") is not None,
            "metricsClient": type(self._ctx.deps.get("metrics_client")).__name__,
            "metricsDeliveryMode": str(self._ctx.cfg.runtime.runtime.metrics_delivery_mode or "").strip().lower() or "buffered",
            "metricsSink": metrics_sink_name(self._ctx.deps.get("metrics_client")),
            "remoteMetricsEnabled": remote_metrics_enabled(self._ctx.deps.get("metrics_client")),
            "monitoringEnabled": bool(
                getattr(self._ctx.cfg.runtime, "monitoring", None)
                and self._ctx.cfg.runtime.monitoring.enabled
            ),
            "monitoringBackend": str(getattr(self._ctx.cfg.runtime.monitoring, "backend", "") or ""),
            "monitoringFolderId": str(getattr(self._ctx.cfg.runtime.monitoring, "folder_id", "") or "").strip()
            or str(self._ctx.cfg.deploy.yandex_cloud.folder_id or "").strip(),
            "dashboardName": str(
                self._ctx.cfg.runtime.monitoring.dashboard_name_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.monitoring.dashboard_name_test
            ).strip(),
            "dashboardId": str(
                self._ctx.cfg.runtime.monitoring.dashboard_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.monitoring.dashboard_id_test
            ).strip(),
            "datalensEnabled": bool(
                getattr(self._ctx.cfg.runtime, "datalens", None)
                and self._ctx.cfg.runtime.datalens.enabled
            ),
            "datalensOrgId": str(getattr(self._ctx.cfg.runtime.datalens, "org_id", "") or "").strip(),
            "datalensWorkbookName": str(getattr(self._ctx.cfg.runtime.datalens, "workbook_name", "") or "").strip(),
            "datalensWorkbookId": str(
                self._ctx.cfg.runtime.datalens.workbook_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.workbook_id_test
            ).strip(),
            "datalensConnectionName": str(
                self._ctx.cfg.runtime.datalens.connection_name_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.connection_name_test
            ).strip(),
            "datalensConnectionId": str(
                self._ctx.cfg.runtime.datalens.connection_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.connection_id_test
            ).strip(),
            "datalensDashboardName": str(
                self._ctx.cfg.runtime.datalens.dashboard_name_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.dashboard_name_test
            ).strip(),
            "datalensDashboardId": str(
                self._ctx.cfg.runtime.datalens.dashboard_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.dashboard_id_test
            ).strip(),
            "datalensDashboardUrl": str(
                self._ctx.cfg.runtime.datalens.dashboard_url_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.dashboard_url_test
            ).strip(),
            "prometheusEnabled": bool(prometheus_cfg and getattr(prometheus_cfg, "enabled", False)),
            "prometheusBackend": str(getattr(prometheus_cfg, "backend", "") or "").strip(),
            "prometheusEndpointWrite": str(getattr(prometheus_cfg, "endpoint_write", "") or "").strip(),
            "prometheusWorkspaceId": str(
                getattr(prometheus_cfg, "workspace_id_prod", "")
                if env_name == "prod"
                else getattr(prometheus_cfg, "workspace_id_test", "")
            ).strip(),
            "grafanaEnabled": bool(grafana_cfg and getattr(grafana_cfg, "enabled", False)),
            "grafanaBaseUrl": str(getattr(grafana_cfg, "public_base_url", "") or "").strip(),
            "grafanaDashboardUid": str(
                getattr(grafana_cfg, "dashboard_uid_prod", "")
                if env_name == "prod"
                else getattr(grafana_cfg, "dashboard_uid_test", "")
            ).strip(),
            "grafanaDashboardUrl": str(
                getattr(grafana_cfg, "dashboard_url_prod", "")
                if env_name == "prod"
                else getattr(grafana_cfg, "dashboard_url_test", "")
            ).strip(),
            "grafanaEmbedUrl": str(
                getattr(grafana_cfg, "embed_url_prod", "")
                if env_name == "prod"
                else getattr(grafana_cfg, "embed_url_test", "")
            ).strip(),
            "bottleneckMetricsLevel": resolve_bottleneck_metrics_level(self._ctx),
            "stageMetricsEnabled": is_stage_metrics_enabled(self._ctx),
            "debugMetricsEnabled": is_debug_metrics_enabled(self._ctx),
            "structuredLoggerEnabled": self._ctx.deps.get("structured_logger") is not None,
            "structuredLogger": type(self._ctx.deps.get("structured_logger")).__name__,
        }
        return {
            "artifact": "dtm_info_dashboard",
            "view": "summary",
            "detailAvailable": {
                "query": "view=detail",
                "paths": ["/info/detail", "/api/v2/info/detail"],
            },
            "snapshot": {
                "env": env_name,
                "error": "",
                "bucket": str(snap_cfg.bucket),
                "rootPrefix": root_prefix,
                "rawKey": raw_key,
                "prepKey": str(snap_cfg.prefix_prep).replace("{env}", env_name),
                "extraPrefix": str(snap_cfg.prefix_extra).replace("{env}", env_name),
                "sourceId": "",
                "sourceHash": "",
                "rawFetchedAt": "",
                "prepBuiltAt": "",
            },
            "counts": {
                "tasksTotal": 0,
                "byStatus": {},
                "detailDeferred": True,
            },
            "storage": {
                "detailDeferred": True,
            },
            "queue": {
                "enabled": bool(queue_cfg.enabled),
                "provider": str(queue_cfg.provider),
                "queueName": queue_name,
                "endpointUrl": str(queue_cfg.endpoint_url or ""),
                "policy": {
                    "retryModel": "queue_driven",
                    "batchPolicy": "per_message",
                    "terminalStatuses": ["failed_terminal"],
                    "retryableStatuses": ["failed_retryable"],
                },
                "latest": {},
                "live": {"detailDeferred": True},
            },
            "build": {
                "functionName": function_name,
                "detailDeferred": True,
            },
            "jobs": {
                "recent": [],
                "failedRecent": [],
                "latestByCommand": {},
                "lastSuccessfulRender": None,
                "lastSuccessfulUpdate": None,
                "detailDeferred": True,
            },
            "renderDebug": {
                "state": "detail_required",
                "reason": "detail_view_required",
                "details": {},
            },
            "telemetry": telemetry_payload,
            "telegram": {
                "webhookPath": webhook_path,
                "webhookUrl": webhook_url,
                "allowedUpdates": list(telegram_cfg.allowed_updates or []),
                "maxConnections": int(telegram_cfg.max_connections),
                "secretRequired": bool(telegram_cfg.secret_required),
                "secretConfigured": bool(str(self._ctx.deps.get("tg_webhook_secret_token", "")).strip()),
            },
            "web": {
                "apiDomain": api_domain,
                "uiBasePath": ui_base_path,
            },
            "attachmentsHarness": {
                "enabled": bool(self._ctx.cfg.runtime.api.get("attachment_harness_enabled", True)),
                "detailDeferred": True,
            },
            "bottlenecks": {
                "profilingLevel": resolve_bottleneck_metrics_level(self._ctx),
                "stageMetricsEnabled": is_stage_metrics_enabled(self._ctx),
                "debugMetricsEnabled": is_debug_metrics_enabled(self._ctx),
                "recentApiTracesDeferred": True,
                "recentDirectApiOuterTracesDeferred": True,
                "recentApiTraces": [],
                "recentDirectApiOuterTraces": [],
            },
        }

    def _detail_payload(self, req: HttpRequest, summary_payload: dict[str, Any]) -> dict[str, Any]:
        payload = json.loads(json.dumps(summary_payload))
        prep = None
        raw = None
        snapshot_error = ""
        try:
            prep = self._get_prep_snapshot()
            raw = self._get_raw_snapshot()
        except Exception as exc:
            snapshot_error = str(exc)
        status_counts: dict[str, int] = {}
        if prep is not None:
            for view in prep.tasks_by_id.values():
                key = str(view.sheet.status or "unknown")
                status_counts[key] = status_counts.get(key, 0) + 1

        env_name = str(payload.get("snapshot", {}).get("env", "")).strip().lower() or "dev"
        snap_cfg = self._ctx.cfg.runtime.snapshot_engine
        queue_cfg = self._ctx.cfg.runtime.queue
        raw_key = str(payload.get("snapshot", {}).get("rawKey", "")).strip() or str(snap_cfg.prefix_raw).replace("{env}", env_name)
        root_prefix = str(payload.get("snapshot", {}).get("rootPrefix", "")).strip() or self._resolve_root_prefix(raw_key)
        storage = self._storage_stats_loader(str(snap_cfg.bucket), root_prefix)
        queue_url = str(queue_cfg.prod_queue_url if env_name == "prod" else queue_cfg.test_queue_url).strip()
        queue_name = queue_url.rstrip("/").rsplit("/", 1)[-1] if queue_url else ""
        status_store = get_command_runtime(self._ctx).status_store
        jobs_payload = {
            "recent": [],
            "failedRecent": [],
            "latestByCommand": {},
            "lastSuccessfulRender": None,
            "lastSuccessfulUpdate": None,
        }
        latest_jobs: dict[str, Any] = {}
        if status_store is not None:
            jobs_payload = self._recent_jobs_payload_builder(status_store)
            latest_jobs = self._latest_jobs_payload_builder(status_store)
            merged_latest = dict(jobs_payload.get("latestByCommand", {}) or {})
            merged_latest.update(latest_jobs)
            jobs_payload["latestByCommand"] = merged_latest
        queue_live = self._queue_live_payload(queue_url) if bool(queue_cfg.enabled) else {}
        build_payload = self._build_payload_loader(env_name)
        latest_render = None
        latest_by_command = dict(jobs_payload.get("latestByCommand", {}) or {})
        candidate = latest_by_command.get("render_timeline_sheet")
        if isinstance(candidate, dict):
            latest_render = JobStatusRecord(
                job_id=str(candidate.get("jobId", "")).strip(),
                command_type=str(candidate.get("commandType", "render_timeline_sheet")).strip(),
                status=str(candidate.get("status", "")).strip(),
                requested_at_utc=(
                    datetime.fromisoformat(str(candidate.get("requestedAt", "")).replace("Z", "+00:00"))
                    if str(candidate.get("requestedAt", "")).strip()
                    else datetime.now(timezone.utc)
                ),
                started_at_utc=(
                    datetime.fromisoformat(str(candidate.get("startedAt", "")).replace("Z", "+00:00"))
                    if str(candidate.get("startedAt", "")).strip()
                    else None
                ),
                finished_at_utc=(
                    datetime.fromisoformat(str(candidate.get("finishedAt", "")).replace("Z", "+00:00"))
                    if str(candidate.get("finishedAt", "")).strip()
                    else None
                ),
                requested_by=dict(candidate.get("requestedBy", {}) or {}),
                summary=dict(candidate.get("summary", {}) or {}),
                warnings=[str(item) for item in list(candidate.get("warnings", []) or [])],
                retryable=bool(candidate.get("retryable", False)),
                error=dict(candidate.get("error", {}) or {}) or None,
            )
        render_debug = self._render_debug_payload_builder(latest_render)
        payload["view"] = "detail"
        payload["snapshot"].update(
            {
                "env": env_name,
                "error": snapshot_error,
                "bucket": str(snap_cfg.bucket),
                "rootPrefix": root_prefix,
                "rawKey": raw_key,
                "prepKey": str(snap_cfg.prefix_prep).replace("{env}", env_name),
                "extraPrefix": str(snap_cfg.prefix_extra).replace("{env}", env_name),
                "sourceId": "" if prep is None else str(prep.source_id),
                "sourceHash": "" if prep is None else str(prep.raw_source_hash),
                "rawFetchedAt": "" if raw is None else raw.fetched_at_utc.astimezone(timezone.utc).isoformat(),
                "prepBuiltAt": "" if prep is None else prep.built_at_utc.astimezone(timezone.utc).isoformat(),
            }
        )
        payload["counts"] = {
            "tasksTotal": 0 if prep is None else len(prep.tasks_by_id),
            "byStatus": status_counts,
        }
        payload["storage"] = storage
        payload["queue"] = {
            "enabled": bool(queue_cfg.enabled),
            "provider": str(queue_cfg.provider),
            "queueName": queue_name,
            "endpointUrl": str(queue_cfg.endpoint_url or ""),
            "policy": {
                "retryModel": "queue_driven",
                "batchPolicy": "per_message",
                "terminalStatuses": ["failed_terminal"],
                "retryableStatuses": ["failed_retryable"],
            },
            "latest": latest_by_command,
            "live": queue_live,
        }
        payload["build"] = build_payload
        payload["jobs"] = jobs_payload
        payload["renderDebug"] = render_debug
        payload["attachmentsHarness"] = self._attachments_harness_builder(req, prep)
        payload["bottlenecks"] = {
            "profilingLevel": resolve_bottleneck_metrics_level(self._ctx),
            "stageMetricsEnabled": is_stage_metrics_enabled(self._ctx),
            "debugMetricsEnabled": is_debug_metrics_enabled(self._ctx),
            "recentApiTraces": RECENT_API_STAGE_EVENTS.recent_traces(limit=8),
            "recentDirectApiOuterTraces": RECENT_DIRECT_API_OUTER_TRACES.recent_traces(limit=8),
        }
        return payload

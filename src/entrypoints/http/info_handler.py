"""Operational info dashboard handler."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import urlparse

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import html_response, json_response
from src.infra.yc_function_info import get_function_build_info
from src.infra.yc_queue_info import get_queue_live_stats
from src.observability.bottlenecks import (
    RECENT_DIRECT_API_OUTER_TRACES,
    RECENT_API_STAGE_EVENTS,
    is_debug_metrics_enabled,
    is_stage_metrics_enabled,
    resolve_bottleneck_metrics_level,
)
from src.snapshot_engine.engine import build_snapshot_engine
from src.worker.model import JobStatusRecord


def _human_size(value: int) -> str:
    size = float(max(0, int(value)))
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.2f} {units[idx]}"


def _iso(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat()


def _job_record_payload(record: JobStatusRecord) -> dict[str, Any]:
    return {
        "jobId": record.job_id,
        "commandType": record.command_type,
        "status": record.status,
        "requestedAt": _iso(record.requested_at_utc),
        "startedAt": _iso(record.started_at_utc),
        "finishedAt": _iso(record.finished_at_utc),
        "requestedBy": dict(record.requested_by),
        "summary": dict(record.summary),
        "warnings": list(record.warnings),
        "retryable": bool(record.retryable),
        "error": dict(record.error or {}) if record.error else None,
    }


def _render_debug_payload(record: JobStatusRecord | None) -> dict[str, Any]:
    if record is None:
        return {
            "lastJobId": "",
            "state": "unknown",
            "reason": "no_render_job_history",
            "details": {},
        }
    summary = dict(record.summary or {})
    warnings = [str(item) for item in list(record.warnings or [])]
    error = dict(record.error or {}) if record.error else {}
    if record.status in {"failed_terminal", "failed_retryable"}:
        if str(error.get("code", "")).strip() == "render_target_unsafe":
            state = "blocked"
            reason = "blocked_by_target_safety_guard"
        else:
            state = "failed"
            reason = str(error.get("code", "")).strip() or "render_job_failed"
    elif record.status == "success":
        if bool(summary.get("render_applied", False)):
            state = "applied"
            reason = "render_applied_successfully"
        else:
            state = "noop"
            reason = warnings[0] if warnings else "render_not_applied"
    elif record.status in {"accepted", "running"}:
        state = "pending"
        reason = f"job_{record.status}"
    else:
        state = "unknown"
        reason = record.status or "unknown"
    return {
        "lastJobId": record.job_id,
        "state": state,
        "reason": reason,
        "details": _job_record_payload(record),
    }


def _load_info_asset(name: str) -> str:
    asset_path = Path(__file__).with_name("templates") / name
    return asset_path.read_text(encoding="utf-8")


_INFO_TEMPLATE = _load_info_asset("info.html")
_INFO_CSS = _load_info_asset("info.css")
_INFO_JS = _load_info_asset("info.js")


def _render_info_page(payload: dict[str, Any]) -> str:
    escaped = escape(json.dumps(payload, ensure_ascii=False))
    return (
        _INFO_TEMPLATE
        .replace("__INFO_CSS__", _INFO_CSS)
        .replace("__INFO_JS__", _INFO_JS)
        .replace("__INFO_PAYLOAD_JSON__", escaped)
    )


class InfoHandler:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def _resolve_ui_base_path(self, req: HttpRequest) -> str:
        raw_event = req.raw_event if isinstance(req.raw_event, dict) else {}
        public_path = ""
        for candidate in (
            raw_event.get("url"),
            raw_event.get("rawPath"),
            raw_event.get("raw_path"),
            raw_event.get("path"),
        ):
            text = str(candidate or "").strip()
            if not text:
                continue
            if text.startswith(("http://", "https://")):
                text = urlparse(text).path or "/"
            public_path = normalize_path(text)
            if public_path:
                break
        normalized_path = normalize_path(req.path)
        if not public_path or not normalized_path:
            return ""
        if public_path == normalized_path:
            return ""
        if public_path.endswith(normalized_path):
            prefix = public_path[: -len(normalized_path)].rstrip("/")
            return prefix if prefix.startswith("/") else f"/{prefix}" if prefix else ""
        return ""

    def _storage_stats(self, bucket: str, root_prefix: str) -> dict[str, Any]:
        try:
            import boto3  # type: ignore
        except Exception:
            return {
                "objectsTotal": 0,
                "bytesTotal": 0,
                "bytesHuman": "n/a",
                "byPrefix": {},
                "error": "boto3_missing",
            }
        endpoint = str(self._ctx.cfg.db.object_storage.get("endpoint_url_default", "")).strip() or None
        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=self._ctx.deps.get("aws_access_key_id"),
            aws_secret_access_key=self._ctx.deps.get("aws_secret_access_key"),
        )
        total_objects = 0
        total_bytes = 0
        by_prefix = {"raw": 0, "prep": 0, "extra": 0, "attachments": 0, "jobs": 0}
        token = None
        while True:
            kwargs = {"Bucket": bucket, "Prefix": root_prefix, "MaxKeys": 1000}
            if token:
                kwargs["ContinuationToken"] = token
            response = client.list_objects_v2(**kwargs)
            for item in response.get("Contents", []) or []:
                key = str(item.get("Key", ""))
                size = int(item.get("Size", 0))
                total_objects += 1
                total_bytes += size
                if "/raw/" in key:
                    by_prefix["raw"] += size
                elif "/prep/" in key:
                    by_prefix["prep"] += size
                elif "/extra/" in key:
                    by_prefix["extra"] += size
                elif "/attachments/" in key:
                    by_prefix["attachments"] += size
                elif "/jobs/" in key:
                    by_prefix["jobs"] += size
            if not response.get("IsTruncated"):
                break
            token = response.get("NextContinuationToken")
        return {
            "objectsTotal": total_objects,
            "bytesTotal": total_bytes,
            "bytesHuman": _human_size(total_bytes),
            "byPrefix": by_prefix,
        }

    def _resolve_root_prefix(self, raw_key: str) -> str:
        parts = [part for part in str(raw_key).split("/") if part]
        if len(parts) >= 2:
            return "/".join(parts[:2]) + "/"
        if parts:
            return parts[0] + "/"
        return ""

    def _latest_jobs_payload(self, status_store: Any) -> dict[str, Any]:
        latest_jobs: dict[str, Any] = {}
        for command_type in (
            "update_snapshot",
            "send_reminders",
            "render_timeline_sheet",
            "render_designers_sheet",
            "group_query_reply",
            "attach_task_file",
        ):
            try:
                record = status_store.get_latest(command_type)
            except Exception:
                record = None
            if record is None:
                continue
            latest_jobs[command_type] = _job_record_payload(record)
        return latest_jobs

    def _recent_jobs_payload(self, status_store: Any) -> dict[str, Any]:
        try:
            recent_records = list(status_store.get_recent(20))
        except Exception as exc:
            return {"recent": [], "failedRecent": [], "error": str(exc)}
        recent_payload = [_job_record_payload(record) for record in recent_records]
        failed_payload = [
            item
            for item in recent_payload
            if str(item.get("status", "")).lower() in {"failed_retryable", "failed_terminal"}
        ]
        latest_by_command: dict[str, Any] = {}
        for item in recent_payload:
            command_type = str(item.get("commandType", "")).strip()
            if command_type and command_type not in latest_by_command:
                latest_by_command[command_type] = item
        last_successful_render = next(
            (
                item
                for item in recent_payload
                if str(item.get("commandType", "")) == "render_timeline_sheet"
                and str(item.get("status", "")).lower() == "success"
                and bool(dict(item.get("summary", {}) or {}).get("render_applied", False))
            ),
            None,
        )
        last_successful_update = next(
            (
                item
                for item in recent_payload
                if str(item.get("commandType", "")) == "update_snapshot"
                and str(item.get("status", "")).lower() == "success"
            ),
            None,
        )
        return {
            "recent": recent_payload,
            "failedRecent": failed_payload,
            "latestByCommand": latest_by_command,
            "lastSuccessfulRender": last_successful_render,
            "lastSuccessfulUpdate": last_successful_update,
        }

    def _queue_live_payload(self, queue_url: str) -> dict[str, Any]:
        if not queue_url:
            return {"error": "queue_url_missing"}
        try:
            stats = get_queue_live_stats(
                queue_url=queue_url,
                endpoint_url=str(self._ctx.cfg.runtime.queue.endpoint_url or "").strip() or None,
                aws_access_key_id=self._ctx.deps.get("aws_access_key_id"),
                aws_secret_access_key=self._ctx.deps.get("aws_secret_access_key"),
            )
        except Exception as exc:
            return {"queue_name": queue_url.rstrip("/").rsplit("/", 1)[-1], "error": str(exc)}
        return stats.to_dict()

    def _build_payload(self, env_name: str) -> dict[str, Any]:
        function_name = str(
            self._ctx.cfg.deploy.yandex_cloud.function_name_prod
            if env_name == "prod"
            else self._ctx.cfg.deploy.yandex_cloud.function_name_test
        ).strip()
        try:
            info = get_function_build_info(
                folder_id=str(self._ctx.cfg.deploy.yandex_cloud.folder_id).strip(),
                function_name=function_name,
                sa_json_credentials=self._ctx.deps.get("yc_sa_json_credentials"),
                sa_key_file=self._ctx.deps.get("yc_sa_key_file"),
            )
        except Exception as exc:
            return {"functionName": function_name, "error": str(exc)}
        return {
            "functionName": info.function_name,
            "activeVersionId": info.active_version_id,
            "deployedAt": info.deployed_at,
            "runtime": info.runtime,
            "memory": info.memory,
            "timeoutSeconds": info.timeout_seconds,
            "entrypoint": info.entrypoint,
            "serviceAccountId": info.service_account_id,
        }

    def _metrics_labels(self, *, env_name: str, view: str) -> dict[str, str]:
        return {
            "env": str(env_name or "").strip() or "unknown",
            "module": "api",
            "operation": f"info.{view}",
        }

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
            "datalensWorkbookName": str(
                getattr(self._ctx.cfg.runtime.datalens, "workbook_name", "") or ""
            ).strip(),
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
            engine = build_snapshot_engine(self._ctx)
            prep = engine._prep_cache.get()  # noqa: SLF001
            raw = engine._raw_cache.get()  # noqa: SLF001
        except Exception as exc:  # pragma: no cover - safety for optional deps/runtime config
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
        storage = self._storage_stats(str(snap_cfg.bucket), root_prefix)
        queue_url = str(queue_cfg.prod_queue_url if env_name == "prod" else queue_cfg.test_queue_url).strip()
        queue_name = queue_url.rstrip("/").rsplit("/", 1)[-1] if queue_url else ""
        status_store = self._ctx.deps.get("job_status_store")
        jobs_payload = {
            "recent": [],
            "failedRecent": [],
            "latestByCommand": {},
            "lastSuccessfulRender": None,
            "lastSuccessfulUpdate": None,
        }
        latest_jobs: dict[str, Any] = {}
        if status_store is not None:
            jobs_payload = self._recent_jobs_payload(status_store)
            latest_jobs = self._latest_jobs_payload(status_store)
            merged_latest = dict(jobs_payload.get("latestByCommand", {}) or {})
            merged_latest.update(latest_jobs)
            jobs_payload["latestByCommand"] = merged_latest
        queue_live = self._queue_live_payload(queue_url) if bool(queue_cfg.enabled) else {}
        build_payload = self._build_payload(env_name)
        latest_render = None
        latest_by_command = dict(jobs_payload.get("latestByCommand", {}) or {})
        if isinstance(latest_by_command, dict):
            candidate = latest_by_command.get("render_timeline_sheet")
            if isinstance(candidate, dict):
                latest_render = JobStatusRecord(
                    job_id=str(candidate.get("jobId", "")).strip(),
                    command_type=str(candidate.get("commandType", "render_timeline_sheet")).strip(),
                    status=str(candidate.get("status", "")).strip(),
                    requested_at_utc=datetime.fromisoformat(
                        str(candidate.get("requestedAt", "")).replace("Z", "+00:00")
                    ) if str(candidate.get("requestedAt", "")).strip() else datetime.now(timezone.utc),
                    started_at_utc=datetime.fromisoformat(
                        str(candidate.get("startedAt", "")).replace("Z", "+00:00")
                    ) if str(candidate.get("startedAt", "")).strip() else None,
                    finished_at_utc=datetime.fromisoformat(
                        str(candidate.get("finishedAt", "")).replace("Z", "+00:00")
                    ) if str(candidate.get("finishedAt", "")).strip() else None,
                    requested_by=dict(candidate.get("requestedBy", {}) or {}),
                    summary=dict(candidate.get("summary", {}) or {}),
                    warnings=[str(item) for item in list(candidate.get("warnings", []) or [])],
                    retryable=bool(candidate.get("retryable", False)),
                    error=dict(candidate.get("error", {}) or {}) or None,
                )
        render_debug = _render_debug_payload(latest_render)
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
        payload["bottlenecks"] = {
            "profilingLevel": resolve_bottleneck_metrics_level(self._ctx),
            "stageMetricsEnabled": is_stage_metrics_enabled(self._ctx),
            "debugMetricsEnabled": is_debug_metrics_enabled(self._ctx),
            "recentApiTraces": RECENT_API_STAGE_EVENTS.recent_traces(limit=8),
            "recentDirectApiOuterTraces": RECENT_DIRECT_API_OUTER_TRACES.recent_traces(limit=8),
        }
        return payload

    def handle(self, req: HttpRequest) -> HttpResponse | None:
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
        env_name = str(self._ctx.cfg.runtime.runtime.env_default).strip().lower() or "dev"
        metrics = self._ctx.deps.get("metrics_client")
        summary_started = perf_counter()
        payload = self._summary_payload(req)
        if metrics is not None:
            metrics.timing(
                "dtm.info.summary.ms",
                (perf_counter() - summary_started) * 1000.0,
                self._metrics_labels(env_name=env_name, view="summary"),
            )
        if detail_mode:
            detail_started = perf_counter()
            payload = self._detail_payload(req, payload)
            if metrics is not None:
                metrics.timing(
                    "dtm.info.detail.ms",
                    (perf_counter() - detail_started) * 1000.0,
                    self._metrics_labels(env_name=env_name, view="detail"),
                )
        as_json = (
            str(req.query.get("format", "")).strip().lower() == "json"
            or path in {"/api/v2/info", "/api/v2/info/detail"}
        )
        if as_json:
            return json_response(200, payload)
        return html_response(200, _render_info_page(payload))

"""Operational info dashboard handler."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from src.contexts.access_api.application.operational_info_read_service import OperationalInfoReadService
from src.platform.context import AppContext
from src.contexts.attachments.public import get_supported_attachment_mime_types
from src.contexts.snapshot.module import get_query_api as _get_snapshot_query_api
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import html_response, json_response
from src.platform.integrations.yandex_cloud.function_info import get_function_build_info
from src.platform.integrations.yandex_cloud.queue_info import get_queue_live_stats
from src.platform.runtime.worker.model import JobStatusRecord


get_snapshot_query_api = _get_snapshot_query_api
get_attachment_mime_types = get_supported_attachment_mime_types


def get_prep_snapshot(ctx):
    snapshot_query = get_snapshot_query_api(ctx)
    getter = getattr(snapshot_query, "get_prep_snapshot", None)
    if callable(getter):
        return getter()
    cache = getattr(snapshot_query, "_prep_cache", None)
    if cache is not None and callable(getattr(cache, "get", None)):
        return cache.get()
    return None


def get_raw_snapshot(ctx):
    snapshot_query = get_snapshot_query_api(ctx)
    getter = getattr(snapshot_query, "get_raw_snapshot", None)
    if callable(getter):
        return getter()
    cache = getattr(snapshot_query, "_raw_cache", None)
    if cache is not None and callable(getattr(cache, "get", None)):
        return cache.get()
    return None


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


class OperationalInfoReadApi:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._service = OperationalInfoReadService(
            ctx,
            resolve_ui_base_path=self._resolve_ui_base_path,
            join_ui_path=self._join_ui_path,
            resolve_root_prefix=self._resolve_root_prefix,
            storage_stats_loader=self._storage_stats,
            queue_live_stats_loader=get_queue_live_stats,
            latest_jobs_payload_builder=self._latest_jobs_payload,
            recent_jobs_payload_builder=self._recent_jobs_payload,
            build_payload_loader=self._build_payload,
            attachments_harness_builder=self._attachments_harness_payload,
            metrics_labels_builder=self._metrics_labels,
            prep_snapshot_getter=lambda: get_prep_snapshot(self._ctx),
            raw_snapshot_getter=lambda: get_raw_snapshot(self._ctx),
            render_debug_payload_builder=_render_debug_payload,
        )

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

    @staticmethod
    def _join_ui_path(base_path: str, suffix: str) -> str:
        base = str(base_path or "").rstrip("/")
        tail = "/" + str(suffix or "").lstrip("/")
        return f"{base}{tail}" if base else tail

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
            "cleanup_job_statuses",
            "update_snapshot",
            "send_reminders",
            "render_timeline_sheet",
            "render_designers_sheet",
            "group_query_reply",
            "attach_task_file",
            "generate_attachment_preview",
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

    def _attachments_harness_payload(self, req: HttpRequest, prep: Any | None = None) -> dict[str, Any]:
        api_cfg = dict(getattr(self._ctx.cfg.runtime, "api", {}) or {})
        enabled = bool(api_cfg.get("attachment_harness_enabled", True))
        probe_task_id = str(api_cfg.get("attachment_harness_probe_task_id", "1111111111") or "").strip()
        expected_status = str(api_cfg.get("attachment_harness_probe_task_status", "test") or "").strip().lower() or "test"
        ui_base_path = self._resolve_ui_base_path(req)
        browser_routes = {
            "requestUpload": self._join_ui_path(ui_base_path, "/auth/attachments/request-upload"),
            "finalize": self._join_ui_path(ui_base_path, "/auth/attachments/finalize"),
            "delete": self._join_ui_path(ui_base_path, "/auth/attachments/delete"),
            "jobStatusTemplate": self._join_ui_path(ui_base_path, "/auth/attachments/jobs/{job_id}"),
            "viewTemplate": self._join_ui_path(ui_base_path, "/auth/attachments/{attachment_id}/view"),
            "downloadTemplate": self._join_ui_path(ui_base_path, "/auth/attachments/{attachment_id}/download"),
        }
        backend_routes = {
            "requestUpload": self._join_ui_path(ui_base_path, "/admin/task-attachments/request-upload"),
            "finalize": self._join_ui_path(ui_base_path, "/admin/task-attachments/finalize"),
            "delete": self._join_ui_path(ui_base_path, "/admin/task-attachments/delete"),
            "jobStatusTemplate": self._join_ui_path(ui_base_path, "/admin/jobs/{job_id}"),
            "viewTemplate": self._join_ui_path(ui_base_path, "/api/task-attachments/{attachment_id}/view"),
            "downloadTemplate": self._join_ui_path(ui_base_path, "/api/task-attachments/{attachment_id}/download"),
        }
        payload: dict[str, Any] = {
            "enabled": enabled,
            "probeTaskId": probe_task_id,
            "probeTaskExpectedStatus": expected_status,
            "probeTaskAvailable": False,
            "probeTaskStatus": "",
            "probeAttachmentsTotal": 0,
            "probeAttachments": [],
            "allowedMimeTypes": sorted(str(item) for item in get_attachment_mime_types()),
            "browserRoutes": browser_routes,
            "backendRoutes": backend_routes,
            "authFacadeRequired": True,
            "notes": [
                "Reserved probe task must exist in the current snapshot.",
                "Browser upload goes directly to the returned Object Storage uploadUrl.",
                "Finalize is async: wait for terminal job state before checking attachment readiness.",
                "Use probeAttachments in this payload as the backend-owned publication check for the reserved task.",
            ],
        }
        if prep is None or not probe_task_id:
            return payload
        probe_view = getattr(prep, "tasks_by_id", {}).get(probe_task_id)
        if probe_view is None:
            payload["failureReason"] = "probe_task_unavailable"
            return payload
        payload["probeTaskAvailable"] = True
        payload["probeTaskStatus"] = str(getattr(getattr(probe_view, "sheet", None), "status", "") or "").strip().lower()
        extra = getattr(probe_view, "extra", None)
        attachments = list(getattr(extra, "attachments", []) or [])
        projected = []
        for item in attachments:
            attachment_id = str(getattr(item, "attachment_id", "") or getattr(item, "id", "") or "").strip()
            projected.append(
                {
                    "id": attachment_id,
                    "name": str(getattr(item, "filename_display", "") or getattr(item, "filename", "") or "").strip(),
                    "mime": str(getattr(item, "mime_type", "") or getattr(item, "mime", "") or "").strip(),
                    "kind": str(getattr(item, "kind", "") or "").strip(),
                    "status": str(getattr(item, "status", "") or "").strip(),
                    "previewState": str(getattr(item, "preview_state", "") or "").strip(),
                    "derivedPreviewRef": str(getattr(item, "derived_preview_ref", "") or "").strip(),
                    "snapshotVisible": bool(getattr(item, "snapshot_visible", False)),
                    "uploadedAt": _iso(getattr(item, "uploaded_at_utc", None)),
                    "links": {
                        "view": browser_routes["viewTemplate"].replace("{attachment_id}", attachment_id),
                        "download": browser_routes["downloadTemplate"].replace("{attachment_id}", attachment_id),
                    },
                }
            )
        payload["probeAttachments"] = projected
        payload["probeAttachmentsTotal"] = len(projected)
        return payload

    def _metrics_labels(self, *, env_name: str, view: str) -> dict[str, str]:
        return {
            "env": str(env_name or "").strip() or "unknown",
            "module": "api",
            "operation": f"info.{view}",
        }

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        request_mode = self._service.resolve_request_mode(req)
        if request_mode is None:
            return None
        payload = self._service.build_payload(req, detail_mode=request_mode.detail_mode)
        if request_mode.as_json:
            return json_response(200, payload)
        return html_response(200, _render_info_page(payload))


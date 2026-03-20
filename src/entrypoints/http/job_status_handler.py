from __future__ import annotations

from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response, json_response
from src.platform.runtime.command_runtime import get_command_runtime


class JobStatusHandler:
    def __init__(self, ctx) -> None:
        self._ctx = ctx

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        if str(req.method or "").strip().upper() != "GET":
            return None
        path = normalize_path(req.path)
        prefix = "/admin/jobs/"
        if not path.startswith(prefix):
            return None
        command_runtime = get_command_runtime(self._ctx)
        if command_runtime.status_store is None:
            return error_response(
                503,
                code="job_status_unavailable",
                message="Job status store is not configured for current environment.",
            )
        job_id = path[len(prefix) :].strip()
        if not job_id:
            return error_response(400, code="job_id_missing", message="Job id is required.")
        record = command_runtime.get(job_id)
        if record is None:
            return error_response(404, code="job_not_found", message="Job status was not found.")
        return json_response(
            200,
            {
                "artifact": "job_status",
                "job_id": record.job_id,
                "command_type": record.command_type,
                "status": record.status,
                "requested_at_utc": record.requested_at_utc.isoformat(),
                "started_at_utc": record.started_at_utc.isoformat() if record.started_at_utc else None,
                "finished_at_utc": record.finished_at_utc.isoformat() if record.finished_at_utc else None,
                "requested_by": dict(record.requested_by),
                "summary": dict(record.summary),
                "warnings": list(record.warnings),
                "retryable": bool(record.retryable),
                "error": dict(record.error or {}) if record.error else None,
            },
        )

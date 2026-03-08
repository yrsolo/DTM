from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.commands.model import Command, RequestedBy
from src.commands.types import (
    RENDER_DESIGNERS_SHEET,
    RENDER_TIMELINE_SHEET,
    SEND_REMINDERS,
    UPDATE_SNAPSHOT,
)
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response, json_response


class AdminQueueHandler:
    def __init__(self, ctx) -> None:
        self._ctx = ctx

    def _producer(self):
        return self._ctx.deps.get("command_queue_producer")

    def _status_store(self):
        return self._ctx.deps.get("job_status_store")

    @staticmethod
    def _requested_by(req: HttpRequest) -> RequestedBy:
        headers = dict(req.headers or {})
        return RequestedBy(
            source="admin",
            user_id=str(headers.get("X-User-Id", "")).strip() or None,
            chat_id=str(headers.get("X-Chat-Id", "")).strip() or None,
        )

    def _enqueue(self, *, command_type: str, payload: dict, req: HttpRequest) -> HttpResponse:
        producer = self._producer()
        status_store = self._status_store()
        if producer is None or status_store is None:
            return error_response(
                503,
                code="queue_unavailable",
                message="Command queue is not configured for current environment.",
            )
        cmd = Command(
            job_id=uuid4().hex,
            type=command_type,
            created_at_utc=datetime.now(timezone.utc),
            requested_by=self._requested_by(req),
            payload=dict(payload),
        )
        producer.send(cmd)
        record = status_store.put_queued(cmd)
        return json_response(
            202,
            {
                "artifact": "command_enqueued",
                "status": "accepted",
                "job_id": cmd.job_id,
                "command_type": cmd.type,
                "queued_at": record.requested_at_utc.isoformat(),
            },
        )

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        if str(req.method or "").strip().upper() != "POST":
            return None
        path = normalize_path(req.path)
        body = dict(req.body or {})
        if path == "/admin/commands/update-snapshot":
            return self._enqueue(
                command_type=UPDATE_SNAPSHOT,
                payload={"force_refresh": bool(body.get("force_refresh", True)), "dry_run": bool(body.get("dry_run", False))},
                req=req,
            )
        if path == "/admin/commands/render-timeline":
            return self._enqueue(
                command_type=RENDER_TIMELINE_SHEET,
                payload={"statuses": list(body.get("statuses", ["work", "pre_done"])), "dry_run": bool(body.get("dry_run", False))},
                req=req,
            )
        if path == "/admin/commands/render-designers":
            return self._enqueue(
                command_type=RENDER_DESIGNERS_SHEET,
                payload={"statuses": list(body.get("statuses", ["work", "pre_done"])), "dry_run": bool(body.get("dry_run", False))},
                req=req,
            )
        if path == "/admin/commands/send-reminders":
            return self._enqueue(
                command_type=SEND_REMINDERS,
                payload={
                    "mode": str(body.get("mode", "morning")).strip().lower() or "morning",
                    "statuses": list(body.get("statuses", ["work", "pre_done"])),
                    "include_today": bool(body.get("include_today", True)),
                    "include_next_workday": bool(body.get("include_next_workday", True)),
                    "force_test_chat": bool(body.get("force_test_chat", False)),
                    "mock_external": bool(body.get("mock_external", False)),
                },
                req=req,
            )
        return None

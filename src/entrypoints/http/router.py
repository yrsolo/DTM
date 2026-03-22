"""HTTP router for index entrypoint."""

from __future__ import annotations

from time import perf_counter

from src.platform.context import AppContext
from src.contexts.access_api.public import (
    get_primary_browser_read_api,
)
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.admin_queue_handler import AdminQueueHandler
from src.entrypoints.http.admin_task_attachments_handler import AdminTaskAttachmentsHandler
from src.entrypoints.http.job_status_handler import JobStatusHandler
from src.contexts.telegram_interaction.public import get_webhook_handler
from src.platform.observability.bottlenecks import append_response_headers


class HttpRouter:
    """Route table based HTTP router."""

    def __init__(self, ctx: AppContext) -> None:
        self._telegram_webhook_handler = get_webhook_handler(ctx)
        self._admin_task_attachments_handler = AdminTaskAttachmentsHandler(ctx)
        self._admin_queue_handler = AdminQueueHandler(ctx)
        self._job_status_handler = JobStatusHandler(ctx)
        self._primary_browser_read_api = get_primary_browser_read_api(ctx)

    @staticmethod
    def _with_headers(response: HttpResponse, extra_headers: dict[str, str]) -> HttpResponse:
        return HttpResponse(
            status=response.status,
            body=response.body,
            headers=append_response_headers(response.headers, extra_headers),
        )

    async def dispatch(self, req: HttpRequest) -> HttpResponse | None:
        trace_id = str((req.headers or {}).get("X-DTM-Trace-Id", "")).strip()
        trace_direct_api = bool(trace_id)
        started_at = perf_counter()
        handlers = [
            ("telegram", self._telegram_webhook_handler.handle),
            ("admin_task_attachments", self._admin_task_attachments_handler.handle),
            ("admin_queue", self._admin_queue_handler.handle),
            ("job_status", self._job_status_handler.handle),
            ("browser_read", self._primary_browser_read_api.handle),
        ]
        for name, handler in handlers:
            precheck_ms = (perf_counter() - started_at) * 1000.0
            handler_started = perf_counter()
            response = handler(req)
            handler_total_ms = (perf_counter() - handler_started) * 1000.0
            if response is None:
                continue
            if not trace_direct_api:
                return response
            router_total_ms = precheck_ms + handler_total_ms
            return self._with_headers(
                response,
                {
                    "X-DTM-Router-Handler-Name": name,
                    "X-DTM-Router-Precheck-Ms": f"{precheck_ms:.3f}",
                    "X-DTM-Router-Handler-Ms": f"{handler_total_ms:.3f}",
                    "X-DTM-Router-Total-Ms": f"{router_total_ms:.3f}",
                },
            )
        return None

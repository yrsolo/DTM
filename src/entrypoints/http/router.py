"""HTTP router for index entrypoint."""

from __future__ import annotations

from typing import Any

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.admin_queue_handler import AdminQueueHandler
from src.entrypoints.http.frontend_compat_handlers import FrontendRootHandler
from src.entrypoints.http.frontend_v2_handler import FrontendV2Handler
from src.entrypoints.http.info_handler import InfoHandler
from src.entrypoints.http.job_status_handler import JobStatusHandler
from src.telegram.webhook import TelegramWebhookHandler


class HttpRouter:
    """Route table based HTTP router."""

    def __init__(self, ctx: AppContext, *, frontend_readmodel_repo_cls: Any) -> None:
        self._telegram_webhook_handler = TelegramWebhookHandler(ctx)
        self._admin_queue_handler = AdminQueueHandler(ctx)
        self._job_status_handler = JobStatusHandler(ctx)
        self._info_handler = InfoHandler(ctx)
        self._frontend_root_handler = FrontendRootHandler(ctx)
        self._frontend_v2_handler = FrontendV2Handler(ctx, frontend_readmodel_repo_cls=frontend_readmodel_repo_cls)

    async def dispatch(self, req: HttpRequest) -> HttpResponse | None:
        telegram_response = self._telegram_webhook_handler.handle(req)
        if telegram_response is not None:
            return telegram_response
        admin_queue_response = self._admin_queue_handler.handle(req)
        if admin_queue_response is not None:
            return admin_queue_response
        job_status_response = self._job_status_handler.handle(req)
        if job_status_response is not None:
            return job_status_response
        info_response = self._info_handler.handle(req)
        if info_response is not None:
            return info_response
        root_response = self._frontend_root_handler.handle(req)
        if root_response is not None:
            return root_response
        return self._frontend_v2_handler.handle(req)

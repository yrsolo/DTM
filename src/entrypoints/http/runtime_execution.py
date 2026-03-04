"""Runtime execution helper for index HTTP entrypoint."""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any

from src.adapters.telegram import TelegramNotifier
from src.app.context import AppContext
from src.entrypoints.http.dto import HttpResponse
from src.entrypoints.http.response_utils import error_response
from src.services.errors import AppError, PermanentError, TransientError, UserError


@dataclass(frozen=True)
class RuntimeExecutionRequest:
    mode: str
    planner_event: Any
    dry_run: bool
    mock_external: Any
    force_refresh: bool


class RuntimeExecutor:
    """Execute planner runtime request and map errors to gateway response."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def execute(self, request: RuntimeExecutionRequest, *, main_func: Any, request_factory: Any, is_http_event: bool) -> HttpResponse:
        deps = self._ctx.deps
        notifier = TelegramNotifier(
            bot_token=str(deps.get("tg_bot_token", "")),
            default_chat_id=deps.get("default_chat_id"),
        )
        try:
            runtime_request = request_factory(
                event=request.planner_event,
                mode=request.mode,
                dry_run=request.dry_run,
                mock_external=request.mock_external,
                force_refresh=request.force_refresh,
            )
            await main_func(runtime_request)
        except Exception as ex:
            if isinstance(ex, UserError):
                error_family = "user"
            elif isinstance(ex, TransientError):
                error_family = "transient"
            elif isinstance(ex, PermanentError):
                error_family = "permanent"
            elif isinstance(ex, AppError):
                error_family = "app"
            else:
                error_family = "unknown"
            tr = str(traceback.format_exc())
            txt = f"Runtime failure:\n{ex}\nTRACEBACK\n{tr}\n"

            print(f"runtime_error_classification={error_family}")
            if isinstance(ex, AppError) and is_http_event:
                status_code = 500
                if isinstance(ex, UserError):
                    status_code = 400
                elif isinstance(ex, TransientError):
                    status_code = 503
                return error_response(
                    status_code,
                    code=ex.code,
                    message=str(ex),
                )
            print(txt)
            try:
                await notifier.alog(txt)
            except Exception as notifier_error:
                print(f"Error notifier failed: {notifier_error}")

            return HttpResponse(status=200, body="!!!EGGORR!!!")

        return HttpResponse(status=200, body="!GOOD!")

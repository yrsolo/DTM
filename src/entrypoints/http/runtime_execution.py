"""Runtime execution helper for index HTTP entrypoint."""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass(frozen=True)
class RuntimeExecutionContext:
    main_func: Callable[..., Awaitable[Any]]
    is_http_event: bool
    app_error_cls: type
    user_error_cls: type
    transient_error_cls: type
    permanent_error_cls: type
    error_response: Callable[..., dict[str, Any]]
    notifier_factory: Callable[[], Any]


@dataclass(frozen=True)
class RuntimeExecutionRequest:
    mode: str
    planner_event: Any
    dry_run: bool
    mock_external: Any
    force_refresh: bool


async def execute_runtime(
    ctx: RuntimeExecutionContext,
    request: RuntimeExecutionRequest,
) -> dict[str, Any]:
    try:
        await ctx.main_func(
            event=request.planner_event,
            mode=request.mode,
            dry_run=request.dry_run,
            mock_external=request.mock_external,
            force_refresh=request.force_refresh,
        )
    except Exception as ex:
        if isinstance(ex, ctx.user_error_cls):
            error_family = "user"
        elif isinstance(ex, ctx.transient_error_cls):
            error_family = "transient"
        elif isinstance(ex, ctx.permanent_error_cls):
            error_family = "permanent"
        elif isinstance(ex, ctx.app_error_cls):
            error_family = "app"
        else:
            error_family = "unknown"
        tr = str(traceback.format_exc())
        txt = f"Runtime failure:\n{ex}\nTRACEBACK\n{tr}\n"

        print(f"runtime_error_classification={error_family}")
        if isinstance(ex, ctx.app_error_cls) and ctx.is_http_event:
            status_code = 500
            if isinstance(ex, ctx.user_error_cls):
                status_code = 400
            elif isinstance(ex, ctx.transient_error_cls):
                status_code = 503
            return ctx.error_response(
                status_code,
                code=ex.code,
                message=str(ex),
            )
        print(txt)
        try:
            await ctx.notifier_factory().alog(txt)
        except Exception as notifier_error:
            print(f"Error notifier failed: {notifier_error}")

        return {
            "statusCode": 200,
            "body": "!!!EGGORR!!!",
        }

    return {
        "statusCode": 200,
        "body": "!GOOD!",
    }

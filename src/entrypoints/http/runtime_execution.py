"""Runtime execution helper for index HTTP entrypoint."""

from __future__ import annotations

import traceback
from typing import Any, Awaitable, Callable


async def execute_runtime(
    *,
    main_func: Callable[..., Awaitable[Any]],
    mode: str,
    planner_event: Any,
    dry_run: bool,
    mock_external: Any,
    force_refresh: bool,
    is_http_event: bool,
    app_error_cls: type,
    user_error_cls: type,
    transient_error_cls: type,
    permanent_error_cls: type,
    error_response: Callable[..., dict[str, Any]],
    notifier_factory: Callable[[], Any],
) -> dict[str, Any]:
    try:
        await main_func(
            event=planner_event,
            mode=mode,
            dry_run=dry_run,
            mock_external=mock_external,
            force_refresh=force_refresh,
        )
    except Exception as ex:
        if isinstance(ex, user_error_cls):
            error_family = "user"
        elif isinstance(ex, transient_error_cls):
            error_family = "transient"
        elif isinstance(ex, permanent_error_cls):
            error_family = "permanent"
        elif isinstance(ex, app_error_cls):
            error_family = "app"
        else:
            error_family = "unknown"
        tr = str(traceback.format_exc())
        txt = f"Runtime failure:\n{ex}\nTRACEBACK\n{tr}\n"

        print(f"runtime_error_classification={error_family}")
        if isinstance(ex, app_error_cls) and is_http_event:
            status_code = 500
            if isinstance(ex, user_error_cls):
                status_code = 400
            elif isinstance(ex, transient_error_cls):
                status_code = 503
            return error_response(
                status_code,
                code=ex.code,
                message=str(ex),
            )
        print(txt)
        try:
            await notifier_factory().alog(txt)
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

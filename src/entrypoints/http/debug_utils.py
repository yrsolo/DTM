"""Debug helpers for HTTP event shape logging."""

from __future__ import annotations

from typing import Any, Callable


def debug_http_shape(
    event: dict[str, Any],
    is_http_event: bool,
    *,
    debug_enabled: bool,
    http_method: Callable[[dict[str, Any]], str],
    http_path: Callable[[dict[str, Any]], str],
    normalize_path: Callable[[str], str],
    query_params: Callable[[dict[str, Any]], dict[str, Any]],
) -> None:
    if not debug_enabled:
        return
    if not isinstance(event, dict):
        print("api_debug non_dict_event")
        return
    request_context = event.get("requestContext")
    rc_keys = sorted(request_context.keys()) if isinstance(request_context, dict) else []
    params = event.get("params")
    params_keys = sorted(params.keys()) if isinstance(params, dict) else []
    qs = query_params(event)
    print(
        "api_debug "
        f"is_http={is_http_event} "
        f"method={http_method(event)!r} "
        f"path={http_path(event)!r} "
        f"norm_path={normalize_path(http_path(event))!r} "
        f"event_keys={sorted(event.keys())} "
        f"request_context_keys={rc_keys} "
        f"params_keys={params_keys} "
        f"query_keys={sorted(qs.keys()) if isinstance(qs, dict) else []}"
    )

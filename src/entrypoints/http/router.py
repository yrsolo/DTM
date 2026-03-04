"""HTTP routing scaffold for index entrypoint delegation."""

from __future__ import annotations

from typing import Any, Callable

HttpHandler = Callable[[dict[str, Any], bool], dict[str, Any] | None]


def dispatch_http(
    event: dict[str, Any],
    is_http_event: bool,
    handlers: tuple[HttpHandler, ...],
) -> dict[str, Any] | None:
    """Run handlers in order and return first non-empty HTTP response."""

    for handler in handlers:
        response = handler(event, is_http_event)
        if response is not None:
            return response
    return None


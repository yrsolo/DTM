"""Thin target handler for explicit top-level mode routing."""

from __future__ import annotations

from typing import Any

from .modes import Mode
from .parse_request import parse_request
from .responses import unknown_route_response


async def handle(
    event: Any,
    _context: Any,
    *,
    handle_http_event,
    handle_queue_event,
    handle_trigger_event,
    get_telegram_webhook_path=lambda: "/telegram",
    get_trigger_modes=lambda: {},
) -> dict[str, Any]:
    """Route by explicit mode and delegate directly to top-level shells."""

    parsed = parse_request(
        event,
        get_trigger_modes=get_trigger_modes,
        get_telegram_webhook_path=get_telegram_webhook_path,
    )
    match parsed.mode:
        case Mode.HEALTHCHECK:
            return {"statusCode": 200, "body": "!HEALTHY!"}
        case (
            Mode.HTTP_ACCESS_API
            | Mode.TELEGRAM_WEBHOOK
        ):
            return await handle_http_event(
                event if isinstance(event, dict) else {},
                parsed.payload,
                True,
            )
        case Mode.QUEUE_WORKER:
            return await handle_queue_event(event)
        case Mode.TRIGGER_TIMER:
            return await handle_trigger_event("timer", event)
        case Mode.TRIGGER_MORNING:
            return await handle_trigger_event("morning", event)
        case Mode.UNKNOWN:
            return unknown_route_response()
        case _:
            return unknown_route_response()

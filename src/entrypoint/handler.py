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
    get_dispatcher,
    triggers: dict[str, str] | None = None,
    telegram_webhook_path: str = "/telegram",
) -> dict[str, Any]:
    """Route by explicit mode and delegate to the transitional dispatcher."""

    parsed = parse_request(
        event,
        triggers=triggers,
        telegram_webhook_path=telegram_webhook_path,
    )
    match parsed.mode:
        case Mode.HEALTHCHECK:
            return {"statusCode": 200, "body": "!HEALTHY!"}
        case (
            Mode.HTTP_ACCESS_API
            | Mode.TELEGRAM_WEBHOOK
            | Mode.QUEUE_WORKER
            | Mode.TRIGGER_TIMER
            | Mode.TRIGGER_MORNING
        ):
            return await get_dispatcher().handle(event, _context)
        case Mode.UNKNOWN:
            return unknown_route_response()
        case _:
            return unknown_route_response()

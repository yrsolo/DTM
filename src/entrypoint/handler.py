"""Thin target handler skeleton for explicit mode routing."""

from __future__ import annotations

from typing import Any

from .modes import Mode
from .parse_request import parse_request
from .responses import unknown_route_response


async def handle(event: Any, _context: Any) -> dict[str, Any]:
    """Keep the target entrypoint import-safe until real routing moves here."""

    parsed = parse_request(event)
    match parsed.mode:
        case Mode.HEALTHCHECK:
            return {"statusCode": 200, "body": "!HEALTHY!"}
        case Mode.UNKNOWN:
            return unknown_route_response()
        case _:
            return unknown_route_response()


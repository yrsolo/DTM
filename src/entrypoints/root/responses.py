"""Helpers for target entrypoint response translation."""

from __future__ import annotations

from typing import Any


def unknown_route_response() -> dict[str, Any]:
    """Default placeholder response for unhandled target entrypoint modes."""

    return {
        "statusCode": 200,
        "body": "!NOOP!",
    }


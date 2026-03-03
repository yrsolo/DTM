"""HTTP event parsing helpers extracted from index entrypoint."""

from __future__ import annotations

import json
from typing import Any


def extract_payload(event: Any) -> tuple[dict[str, Any], bool]:
    """Extract request payload and detect HTTP-like events."""

    if not isinstance(event, dict):
        return {}, False
    is_http = any(
        key in event
        for key in (
            "httpMethod",
            "method",
            "requestMethod",
            "path",
            "rawPath",
            "raw_path",
            "requestContext",
            "queryStringParameters",
            "rawQueryString",
            "params",
            "url",
        )
    )
    if "body" not in event:
        return event, is_http

    raw_body = event.get("body")
    if isinstance(raw_body, dict):
        return raw_body, True
    if isinstance(raw_body, str) and raw_body.strip():
        try:
            parsed = json.loads(raw_body)
            if isinstance(parsed, dict):
                return parsed, True
        except json.JSONDecodeError:
            pass
    return {}, True


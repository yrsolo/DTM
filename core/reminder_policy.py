"""Pure helper policies for reminder pipeline."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover
    aiohttp = None  # type: ignore

try:
    import httpx  # type: ignore
except Exception:  # pragma: no cover
    httpx = None  # type: ignore


def sanitize_proxy_url(url: str | None) -> str | None:
    if not url:
        return None
    return str(url).strip().strip('"').strip("'")


def normalize_chat_messages(messages: Any) -> list[dict[str, str]]:
    """Return chat messages as normalized role/content dictionaries."""
    if isinstance(messages, str):
        return [{"role": "user", "content": messages}]
    if not isinstance(messages, list):
        return []

    normalized: list[dict[str, str]] = []
    for item in messages:
        if not isinstance(item, Mapping):
            continue
        role = str(item.get("role", "user"))
        content = str(item.get("content", ""))
        normalized.append({"role": role, "content": content})
    return normalized


def extract_status_code(error: Exception) -> int | None:
    status_code = getattr(error, "status_code", None)
    if status_code is None:
        response = getattr(error, "response", None)
        if response is not None:
            status_code = getattr(response, "status_code", None)
    try:
        return int(status_code) if status_code is not None else None
    except (TypeError, ValueError):
        return None


def is_transient_llm_error(error: Exception) -> bool:
    transient_types: tuple[type[Any], ...] = (asyncio.TimeoutError, TimeoutError)
    if aiohttp is not None:
        transient_types = transient_types + (aiohttp.ClientError,)  # type: ignore[attr-defined]
    if httpx is not None:
        transient_types = transient_types + (httpx.TransportError,)  # type: ignore[attr-defined]

    if isinstance(error, transient_types):
        return True
    status_code = extract_status_code(error)
    if status_code in {408, 425, 429, 500, 502, 503, 504}:
        return True
    error_text = str(error).lower()
    return any(
        token in error_text
        for token in (
            "timeout",
            "timed out",
            "temporary",
            "temporarily",
            "rate limit",
            "too many requests",
            "bad gateway",
            "service unavailable",
            "gateway timeout",
        )
    )


def classify_delivery_error(error: Exception) -> dict[str, Any]:
    transient_types: tuple[type[Any], ...] = (asyncio.TimeoutError, TimeoutError)
    if aiohttp is not None:
        transient_types = transient_types + (aiohttp.ClientError,)  # type: ignore[attr-defined]
    if httpx is not None:
        transient_types = transient_types + (httpx.TransportError,)  # type: ignore[attr-defined]

    if isinstance(error, transient_types):
        return {"is_transient": True, "kind": "timeout_or_transport"}
    error_name = type(error).__name__
    if error_name in {"TimedOut", "NetworkError"}:
        return {"is_transient": True, "kind": "network_error_name"}
    if error_name == "RetryAfter":
        return {"is_transient": True, "kind": "rate_limit_name"}

    retry_after = getattr(error, "retry_after", None)
    if retry_after is not None:
        return {"is_transient": True, "kind": "rate_limit_attr"}

    status_code = extract_status_code(error)
    if status_code in {408, 425, 429, 500, 502, 503, 504}:
        return {"is_transient": True, "kind": f"http_{status_code}"}
    if status_code in {400, 401, 403, 404}:
        return {"is_transient": False, "kind": f"http_{status_code}"}

    error_text = str(error).lower()
    transient_markers = (
        "timeout",
        "timed out",
        "temporary",
        "temporarily",
        "rate limit",
        "too many requests",
        "connection reset",
        "connection aborted",
        "connection refused",
        "bad gateway",
        "service unavailable",
        "gateway timeout",
    )
    if any(marker in error_text for marker in transient_markers):
        return {"is_transient": True, "kind": "message_transient"}

    permanent_markers = (
        "chat not found",
        "bot was blocked",
        "forbidden",
        "bad request",
        "can't parse entities",
        "message is too long",
    )
    if any(marker in error_text for marker in permanent_markers):
        return {"is_transient": False, "kind": "message_permanent"}

    return {"is_transient": False, "kind": "unknown"}

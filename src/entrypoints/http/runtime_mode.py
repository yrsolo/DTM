"""Runtime mode extraction helpers for HTTP/non-HTTP entrypoint flow."""

from __future__ import annotations

from typing import Any, Callable


def resolve_trigger_mode(event: Any, triggers: dict[str, str]) -> str:
    try:
        messages = event.get("messages")
        trigger_id = str(messages[0]["details"]["trigger_id"]).strip()
    except (TypeError, KeyError, IndexError):
        return ""
    return str(triggers.get(trigger_id, "")).strip().lower()


def extract_run_mode(
    event: dict[str, Any],
    request_payload: dict[str, Any],
    is_http_event: bool,
    *,
    allowed_run_modes: set[str] | frozenset[str],
    query_params: Callable[[dict[str, Any]], dict[str, Any]],
) -> str:
    raw_mode = str(request_payload.get("mode", "")).strip().lower()
    if not raw_mode and is_http_event:
        params = query_params(event)
        raw_mode = str(params.get("mode", "")).strip().lower()
    if raw_mode not in allowed_run_modes:
        return ""
    return raw_mode


def extract_force_refresh(
    event: dict[str, Any],
    request_payload: dict[str, Any],
    is_http_event: bool,
    *,
    query_params: Callable[[dict[str, Any]], dict[str, Any]],
    parse_bool: Callable[[str | None, bool], bool],
) -> bool:
    payload_value = request_payload.get("force_refresh")
    if payload_value is not None:
        return parse_bool(str(payload_value), False)
    if is_http_event:
        params = query_params(event)
        return parse_bool(params.get("force_refresh"), False)
    return False

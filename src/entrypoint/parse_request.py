"""Target parsed-request contract for top-level entrypoint routing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.commands.yandex_mq import is_message_queue_event
from src.entrypoints.http.event_parser import extract_payload, http_method, http_path, normalize_path

from .modes import Mode


@dataclass(frozen=True, slots=True)
class ParsedRequest:
    """Normalized request/event data for explicit mode routing."""

    mode: Mode
    path: str = ""
    method: str = ""
    source: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    raw_event_hints: dict[str, Any] = field(default_factory=dict)


def _trigger_id(event: Any) -> str:
    if not isinstance(event, dict):
        return ""
    messages = event.get("messages")
    if not isinstance(messages, list) or not messages:
        return ""
    first = messages[0]
    if not isinstance(first, dict):
        return ""
    details = first.get("details")
    if not isinstance(details, dict):
        return ""
    return str(details.get("trigger_id", "")).strip()


def parse_request(
    event: Any,
    *,
    get_trigger_modes=None,
    get_telegram_webhook_path=None,
) -> ParsedRequest:
    """Classify the incoming event into an explicit top-level mode."""

    if is_message_queue_event(event):
        return ParsedRequest(
            mode=Mode.QUEUE_WORKER,
            source="queue",
            raw_event_hints={"event_type": "message_queue"},
        )

    payload, is_http_event = extract_payload(event)
    payload = dict(payload or {})
    if bool(payload.get("healthcheck")):
        return ParsedRequest(
            mode=Mode.HEALTHCHECK,
            source="healthcheck",
            payload=payload,
            raw_event_hints={"event_type": "healthcheck"},
        )

    if is_http_event and isinstance(event, dict):
        path = normalize_path(http_path(event))
        method = http_method(event)
        telegram_webhook_path = (
            get_telegram_webhook_path()
            if callable(get_telegram_webhook_path)
            else "/telegram"
        )
        telegram_path = normalize_path(str(telegram_webhook_path or "").strip() or "/telegram")
        mode = Mode.TELEGRAM_WEBHOOK if path in {telegram_path, "/telegram/webhook"} else Mode.HTTP_ACCESS_API
        return ParsedRequest(
            mode=mode,
            path=path,
            method=method,
            source="http",
            payload=payload,
            raw_event_hints={"event_type": "http"},
        )

    trigger_lookup = dict(get_trigger_modes() or {}) if callable(get_trigger_modes) else {}
    trigger_id = _trigger_id(event)
    trigger_mode = str(trigger_lookup.get(trigger_id, "")).strip().lower()
    if trigger_mode == "timer":
        return ParsedRequest(
            mode=Mode.TRIGGER_TIMER,
            source="trigger",
            payload=payload,
            raw_event_hints={"trigger_id": trigger_id, "trigger_mode": trigger_mode},
        )
    if trigger_mode == "morning":
        return ParsedRequest(
            mode=Mode.TRIGGER_MORNING,
            source="trigger",
            payload=payload,
            raw_event_hints={"trigger_id": trigger_id, "trigger_mode": trigger_mode},
        )

    return ParsedRequest(
        mode=Mode.UNKNOWN,
        payload=payload,
        raw_event_hints={"event_type": "unknown"},
    )

"""Incoming event classification for top-level entrypoint dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.platform.runtime.commands.yandex_mq import is_message_queue_event
from src.entrypoints.http.event_parser import extract_payload
from src.entrypoints.http.runtime_mode import resolve_trigger_mode


class EventKind(str, Enum):
    QUEUE = "queue"
    HTTP = "http"
    HEALTHCHECK = "healthcheck"
    TRIGGER = "trigger"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class EventClassification:
    kind: EventKind
    request_payload: dict[str, Any]
    is_http_event: bool
    trigger_mode: str


def classify_event(event: Any, triggers: dict[str, str]) -> EventClassification:
    if is_message_queue_event(event):
        return EventClassification(
            kind=EventKind.QUEUE,
            request_payload={},
            is_http_event=False,
            trigger_mode="",
        )
    request_payload, is_http_event = extract_payload(event)
    if request_payload.get("healthcheck"):
        return EventClassification(
            kind=EventKind.HEALTHCHECK,
            request_payload=request_payload,
            is_http_event=is_http_event,
            trigger_mode="",
        )
    trigger_mode = resolve_trigger_mode(event if isinstance(event, dict) else {}, triggers)
    if is_http_event:
        kind = EventKind.HTTP
    elif trigger_mode:
        kind = EventKind.TRIGGER
    else:
        kind = EventKind.UNKNOWN
    return EventClassification(
        kind=kind,
        request_payload=request_payload,
        is_http_event=is_http_event,
        trigger_mode=trigger_mode,
    )


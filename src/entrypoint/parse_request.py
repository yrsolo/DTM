"""Target parsed-request contract for top-level entrypoint routing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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


def parse_request(event: Any) -> ParsedRequest:
    """Return an import-safe placeholder until real mode extraction moves here."""

    return ParsedRequest(mode=Mode.UNKNOWN)


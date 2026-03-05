"""HTTP DTO contracts for entrypoint router/handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class HttpRequest:
    method: str
    path: str
    query: dict[str, Any] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, Any] = field(default_factory=dict)
    raw_event: dict[str, Any] = field(default_factory=dict)
    is_http_event: bool = False


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    body: str
    headers: dict[str, str] = field(default_factory=dict)


def to_gateway_response(response: HttpResponse) -> dict[str, Any]:
    return {
        "statusCode": int(response.status),
        "headers": dict(response.headers),
        "body": response.body,
    }

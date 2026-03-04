"""Compatibility bindings for legacy core helpers used by HTTP entrypoint."""

from __future__ import annotations

from core.api_payload_v2 import build_frontend_api_payload_v2
from core.group_query import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)

__all__ = [
    "build_frontend_api_payload_v2",
    "build_deadlines_reply",
    "build_tasks_reply",
    "parse_group_query_request",
]

"""Schema snapshot builder for read-model consumer checks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    """Return UTC timestamp in canonical schema artifact format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _type_name(value: Any) -> str:
    """Map runtime value to stable schema type label."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def _collect_schema(value: Any) -> Any:
    """Build recursive deterministic schema signature for JSON-like payload."""
    if isinstance(value, dict):
        return {key: _collect_schema(value[key]) for key in sorted(value.keys())}
    if isinstance(value, list):
        if not value:
            return {"type": "list", "items": "unknown"}
        return {"type": "list", "items": _collect_schema(value[0])}
    return _type_name(value)


def build_schema_snapshot(read_model: dict[str, Any], build_id: str | None = None) -> dict[str, Any]:
    """Build minimal deterministic schema snapshot from read-model payload."""
    source = dict(read_model.get("source", {}))
    return {
        "artifact": "read_model_schema_snapshot",
        "generated_at_utc": _utc_now_iso(),
        "schema_version": read_model.get("schema_version", "unknown"),
        "source_build_id": source.get("build_id") or build_id or "",
        "required_top_level_fields": sorted(read_model.keys()),
        "schema": _collect_schema(read_model),
    }


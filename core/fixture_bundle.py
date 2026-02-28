"""Frontend fixture bundle builder from baseline read-model artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    """Return UTC timestamp in canonical artifact format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_list(value: Any) -> list[Any]:
    """Return list value or empty list fallback."""
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    """Return dict value or empty dict fallback."""
    return value if isinstance(value, dict) else {}


def _trim_list(values: list[Any], limit: int) -> list[Any]:
    """Return list prefix capped by non-negative limit."""
    return list(values[: max(limit, 0)])


def _trim_dict_items(values: dict[str, Any], limit: int) -> dict[str, Any]:
    """Return dict subset preserving insertion order up to limit keys."""
    keys = list(values.keys())[: max(limit, 0)]
    return {key: values[key] for key in keys}


def build_fixture_bundle(
    read_model: dict[str, Any],
    schema_snapshot: dict[str, Any],
    *,
    bundle_id: str = "",
    item_limit: int = 20,
) -> dict[str, Any]:
    """Build reduced fixture payload for frontend integration checks."""
    board = dict(read_model.get("board", {}))
    timeline = _safe_list(board.get("timeline", []))
    by_designer = _safe_dict(board.get("by_designer", {}))
    task_details = _safe_list(read_model.get("task_details", []))

    return {
        "artifact": "frontend_fixture_bundle",
        "generated_at_utc": _utc_now_iso(),
        "bundle_id": bundle_id or read_model.get("source", {}).get("build_id", ""),
        "schema_version": read_model.get("schema_version", "unknown"),
        "source": read_model.get("source", {}),
        "counts": {
            "timeline_total": len(timeline),
            "task_details_total": len(task_details),
            "designers_total": len(by_designer),
            "item_limit": item_limit,
        },
        "sample": {
            "timeline": _trim_list(timeline, item_limit),
            "task_details": _trim_list(task_details, item_limit),
            "by_designer": _trim_dict_items(by_designer, item_limit),
            "alerts": read_model.get("alerts", {}),
            "quality_summary": read_model.get("quality_summary", {}),
        },
        "schema_snapshot": {
            "schema_version": schema_snapshot.get("schema_version"),
            "required_top_level_fields": schema_snapshot.get("required_top_level_fields", []),
            "schema": schema_snapshot.get("schema", {}),
        },
    }


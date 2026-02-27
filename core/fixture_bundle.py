"""Frontend fixture bundle builder from baseline read-model artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _trim_list(values: list[Any], limit: int) -> list[Any]:
    return list(values[: max(limit, 0)])


def _trim_dict_items(values: dict[str, Any], limit: int) -> dict[str, Any]:
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
    timeline = board.get("timeline", [])
    by_designer = board.get("by_designer", {})

    return {
        "artifact": "frontend_fixture_bundle",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "bundle_id": bundle_id or read_model.get("source", {}).get("build_id", ""),
        "schema_version": read_model.get("schema_version", "unknown"),
        "source": read_model.get("source", {}),
        "counts": {
            "timeline_total": len(timeline) if isinstance(timeline, list) else 0,
            "task_details_total": len(read_model.get("task_details", []))
            if isinstance(read_model.get("task_details", []), list)
            else 0,
            "designers_total": len(by_designer) if isinstance(by_designer, dict) else 0,
            "item_limit": item_limit,
        },
        "sample": {
            "timeline": _trim_list(timeline if isinstance(timeline, list) else [], item_limit),
            "task_details": _trim_list(
                read_model.get("task_details", [])
                if isinstance(read_model.get("task_details", []), list)
                else [],
                item_limit,
            ),
            "by_designer": _trim_dict_items(
                by_designer if isinstance(by_designer, dict) else {},
                item_limit,
            ),
            "alerts": read_model.get("alerts", {}),
            "quality_summary": read_model.get("quality_summary", {}),
        },
        "schema_snapshot": {
            "schema_version": schema_snapshot.get("schema_version"),
            "required_top_level_fields": schema_snapshot.get("required_top_level_fields", []),
            "schema": schema_snapshot.get("schema", {}),
        },
    }


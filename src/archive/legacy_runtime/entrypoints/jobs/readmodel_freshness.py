"""DEPRECATED: reference-only readmodel freshness helper."""

from __future__ import annotations

from datetime import datetime, timezone


def safe_print(text: str) -> None:
    print(str(text).encode("ascii", "backslashreplace").decode("ascii"))


def build_readmodel_freshness_marker(row: object | None) -> dict[str, object]:
    if row is None:
        return {
            "available": False,
            "readmodel_id": "frontend_v2:default",
            "generated_at_utc": None,
            "age_seconds": None,
            "built_from_source_hash": "",
            "payload_hash": "",
        }
    generated_at = getattr(row, "generated_at_utc", None)
    age_seconds = None
    if isinstance(generated_at, datetime):
        age_seconds = int((datetime.now(timezone.utc) - generated_at).total_seconds())
    return {
        "available": True,
        "readmodel_id": getattr(row, "readmodel_id", "frontend_v2:default"),
        "generated_at_utc": generated_at.isoformat() if isinstance(generated_at, datetime) else None,
        "age_seconds": age_seconds,
        "built_from_source_hash": str(getattr(row, "built_from_source_hash", "") or ""),
        "payload_hash": str(getattr(row, "payload_hash", "") or ""),
    }

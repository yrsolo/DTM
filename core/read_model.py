"""Stage 6 read-model builder from current runtime artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


READ_MODEL_SCHEMA_VERSION = "1.0.0"


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_alert(alert_evaluation: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not alert_evaluation:
        return []
    level = str(alert_evaluation.get("level", "UNKNOWN"))
    reason = str(alert_evaluation.get("reason", ""))
    source_file = alert_evaluation.get("source_file")
    summary = dict(alert_evaluation.get("summary", {}))
    code = f"alert_level_{level.lower()}"
    return [
        {
            "level": level,
            "code": code,
            "message": reason,
            "source_file": source_file,
            "metrics": summary,
        }
    ]


def build_read_model(
    quality_report: dict[str, Any],
    alert_evaluation: dict[str, Any] | None = None,
    *,
    build_id: str | None = None,
) -> dict[str, Any]:
    report = dict(quality_report or {})
    summary = dict(report.get("summary", {}))
    mode = report.get("mode")
    dry_run = bool(report.get("dry_run", False))

    return {
        "schema_version": READ_MODEL_SCHEMA_VERSION,
        "generated_at_utc": _now_utc_iso(),
        "source": {
            "mode": mode,
            "dry_run": dry_run,
            "build_id": build_id,
        },
        "board": {
            "timeline": [],
            "by_designer": [],
        },
        "task_details": [],
        "alerts": _normalize_alert(alert_evaluation),
        "quality_summary": summary,
    }

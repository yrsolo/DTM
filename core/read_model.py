"""Stage 6 read-model builder from current runtime artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


READ_MODEL_SCHEMA_VERSION = "1.0.0"
REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "generated_at_utc",
    "source",
    "board",
    "task_details",
    "alerts",
    "quality_summary",
)


def _now_utc_iso() -> str:
    """Return UTC timestamp in canonical read-model format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_alert(alert_evaluation: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Normalize optional evaluator payload into read-model alerts list."""
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
    """Build canonical consumer-facing read model from runtime diagnostics."""
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


def validate_read_model_contract(payload: dict[str, Any]) -> list[str]:
    """Validate read-model contract expected by prototype consumers."""
    errors: list[str] = []
    model = dict(payload or {})

    for key in REQUIRED_TOP_LEVEL_FIELDS:
        if key not in model:
            errors.append(f"missing_top_level_field:{key}")

    if model.get("schema_version") != READ_MODEL_SCHEMA_VERSION:
        errors.append("invalid_schema_version")

    generated = model.get("generated_at_utc")
    if not isinstance(generated, str) or not generated.endswith("Z"):
        errors.append("invalid_generated_at_utc")

    source = model.get("source")
    if not isinstance(source, dict):
        errors.append("invalid_source")
    else:
        for key in ("mode", "dry_run", "build_id"):
            if key not in source:
                errors.append(f"missing_source_field:{key}")
        if "dry_run" in source and not isinstance(source.get("dry_run"), bool):
            errors.append("invalid_source_dry_run_type")

    board = model.get("board")
    if not isinstance(board, dict):
        errors.append("invalid_board")
    else:
        for key in ("timeline", "by_designer"):
            if key not in board:
                errors.append(f"missing_board_field:{key}")
            elif not isinstance(board.get(key), list):
                errors.append(f"invalid_board_field_type:{key}")

    if not isinstance(model.get("task_details"), list):
        errors.append("invalid_task_details_type")
    if not isinstance(model.get("alerts"), list):
        errors.append("invalid_alerts_type")
    if not isinstance(model.get("quality_summary"), dict):
        errors.append("invalid_quality_summary_type")

    return errors

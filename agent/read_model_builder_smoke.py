"""Deterministic smoke checks for Stage 6 read-model builder."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.read_model import READ_MODEL_SCHEMA_VERSION, build_read_model


def run() -> None:
    quality_report = {
        "mode": "reminders-only",
        "dry_run": True,
        "summary": {
            "task_row_issue_count": 1,
            "people_row_issue_count": 0,
            "timing_parse_error_count": 2,
            "reminder_sent_count": 3,
            "reminder_send_error_count": 1,
            "reminder_delivery_rate": 0.75,
            "reminder_failure_rate": 0.25,
        },
    }
    alert_evaluation = {
        "level": "WARN",
        "reason": "Warning threshold breached: delivery_rate=0.75.",
        "source_file": "artifacts/tmp/quality_report.json",
        "summary": {
            "reminder_delivery_attemptable_count": 4,
            "reminder_delivery_rate": 0.75,
            "reminder_send_error_count": 1,
        },
    }

    read_model = build_read_model(
        quality_report=quality_report,
        alert_evaluation=alert_evaluation,
        build_id="smoke-build",
    )

    assert read_model["schema_version"] == READ_MODEL_SCHEMA_VERSION, read_model
    assert read_model["source"]["mode"] == "reminders-only", read_model
    assert read_model["source"]["dry_run"] is True, read_model
    assert read_model["source"]["build_id"] == "smoke-build", read_model
    assert isinstance(read_model["generated_at_utc"], str) and read_model["generated_at_utc"].endswith("Z"), read_model
    assert read_model["board"]["timeline"] == [], read_model
    assert read_model["board"]["by_designer"] == [], read_model
    assert read_model["task_details"] == [], read_model
    assert read_model["quality_summary"]["reminder_sent_count"] == 3, read_model
    assert len(read_model["alerts"]) == 1, read_model
    assert read_model["alerts"][0]["level"] == "WARN", read_model
    assert read_model["alerts"][0]["code"] == "alert_level_warn", read_model

    print("read_model_builder_smoke_ok")


if __name__ == "__main__":
    run()

"""Deterministic smoke checks for reminder_alert_evaluator."""

from __future__ import annotations

import tempfile
from pathlib import Path
import json
import sys
import time

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.reminder_alert_evaluator import evaluate_thresholds, find_latest_quality_report


def _write_quality_report(path: Path, attemptable: int, delivery_rate, send_errors: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": "reminders-only",
        "summary": {
            "reminder_delivery_attemptable_count": attemptable,
            "reminder_delivery_rate": delivery_rate,
            "reminder_send_error_count": send_errors,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run() -> None:
    info = evaluate_thresholds({"summary": {"reminder_delivery_attemptable_count": 2}})
    assert info["level"] == "INFO_ONLY", info

    warn = evaluate_thresholds(
        {"summary": {"reminder_delivery_attemptable_count": 10, "reminder_delivery_rate": 0.97, "reminder_send_error_count": 0}}
    )
    assert warn["level"] == "WARN", warn

    critical_rate = evaluate_thresholds(
        {"summary": {"reminder_delivery_attemptable_count": 10, "reminder_delivery_rate": 0.9, "reminder_send_error_count": 0}}
    )
    assert critical_rate["level"] == "CRITICAL", critical_rate

    critical_errors = evaluate_thresholds(
        {"summary": {"reminder_delivery_attemptable_count": 10, "reminder_delivery_rate": 1.0, "reminder_send_error_count": 4}}
    )
    assert critical_errors["level"] == "CRITICAL", critical_errors

    ok = evaluate_thresholds(
        {"summary": {"reminder_delivery_attemptable_count": 10, "reminder_delivery_rate": 0.99, "reminder_send_error_count": 0}}
    )
    assert ok["level"] == "OK", ok

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        first = root / "a" / "quality_report.json"
        second = root / "b" / "quality_report.json"
        _write_quality_report(first, attemptable=10, delivery_rate=0.99, send_errors=0)
        time.sleep(0.02)
        _write_quality_report(second, attemptable=10, delivery_rate=0.94, send_errors=0)
        latest = find_latest_quality_report(root)
        assert latest == second, (latest, second)

    print("reminder_alert_evaluator_smoke_ok")


if __name__ == "__main__":
    run()

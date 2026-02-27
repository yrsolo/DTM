"""Deterministic smoke checks for reminder_alert_evaluator."""

from __future__ import annotations

import tempfile
from pathlib import Path
import json
import sys
import time
import io
from contextlib import redirect_stdout

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.reminder_alert_evaluator import (
    evaluate_thresholds,
    find_latest_quality_report,
    maybe_notify_owner,
    resolve_fail_on,
    should_fail,
    should_notify,
)


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
    assert should_notify("WARN", "warn") is True
    assert should_notify("CRITICAL", "critical") is True
    assert should_notify("WARN", "critical") is False
    assert resolve_fail_on("local", None) == "none"
    assert resolve_fail_on("ci", None) == "warn"
    assert resolve_fail_on("ci", "critical") == "critical"
    assert should_fail("WARN", resolve_fail_on("ci", None)) is True
    assert should_fail("CRITICAL", resolve_fail_on("local", None)) is False

    dry_run_stdout = io.StringIO()
    with redirect_stdout(dry_run_stdout):
        dry_run_notified = maybe_notify_owner(
            alert_evaluation={
                "level": "CRITICAL",
                "reason": "smoke",
                "source_file": "tmp/quality_report.json",
                "summary": {
                    "reminder_delivery_attemptable_count": 10,
                    "reminder_delivery_rate": 0.9,
                    "reminder_send_error_count": 4,
                },
            },
            notify_on="critical",
            notify_context="smoke",
            notify_dry_run=True,
        )
    assert dry_run_notified is True
    rendered = dry_run_stdout.getvalue()
    assert "Критический уровень" in rendered, rendered
    assert "\\u041a" not in rendered, rendered

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

"""Smoke for alert evaluator wiring into local run review flow helpers."""

from pathlib import Path
import json
import sys
import tempfile

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from local_run import build_alert_evaluation, persist_alert_evaluation
from agent.reminder_alert_evaluator import should_fail


def run():
    info_report = {
        "mode": "reminders-only",
        "summary": {
            "reminder_delivery_attemptable_count": 1,
            "reminder_delivery_rate": None,
            "reminder_send_error_count": 0,
        },
    }
    critical_report = {
        "mode": "reminders-only",
        "summary": {
            "reminder_delivery_attemptable_count": 10,
            "reminder_delivery_rate": 0.9,
            "reminder_send_error_count": 0,
        },
    }

    info_eval = build_alert_evaluation(info_report)
    assert info_eval["level"] == "INFO_ONLY", info_eval
    assert should_fail(info_eval["level"], "critical") is False

    critical_eval = build_alert_evaluation(critical_report)
    assert critical_eval["level"] == "CRITICAL", critical_eval
    assert should_fail(critical_eval["level"], "critical") is True

    with tempfile.TemporaryDirectory() as tmp_dir:
        out = Path(tmp_dir) / "alert_evaluation.json"
        persist_alert_evaluation(critical_eval, out)
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["level"] == "CRITICAL", payload
        assert "reason" in payload, payload

    print("reminder_alert_review_flow_smoke_ok")


if __name__ == "__main__":
    run()

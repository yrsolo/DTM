"""Local smoke for derived reminder SLI summary fields."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.planner import build_reminder_sli_summary

BASE_COUNTERS = {
    "sent": 6,
    "send_errors": 2,
    "skipped_duplicate": 1,
    "skipped_no_message": 3,
    "skipped_no_person": 4,
    "skipped_no_chat_id": 5,
    "skipped_vacation": 6,
    "skipped_mock": 7,
}
EXPECTED_ATTEMPTABLE = 9
EXPECTED_ATTEMPTED = 8


def run() -> None:
    """Execute SLI summary derivation checks for reminder counters."""

    summary = build_reminder_sli_summary(BASE_COUNTERS)
    assert summary["reminder_delivery_attemptable_count"] == EXPECTED_ATTEMPTABLE, summary
    assert summary["reminder_delivery_attempted_count"] == EXPECTED_ATTEMPTED, summary
    assert summary["reminder_delivery_rate"] == round(6 / EXPECTED_ATTEMPTABLE, 4), summary
    assert summary["reminder_failure_rate"] == round(2 / EXPECTED_ATTEMPTABLE, 4), summary

    summary_empty = build_reminder_sli_summary({})
    assert summary_empty["reminder_delivery_attemptable_count"] == 0, summary_empty
    assert summary_empty["reminder_delivery_rate"] is None, summary_empty
    assert summary_empty["reminder_failure_rate"] is None, summary_empty
    print("reminder_sli_summary_smoke_ok")


if __name__ == "__main__":
    run()

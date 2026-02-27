"""Local smoke for persisted reminder SLI trend snapshots."""

from pathlib import Path
import json
import sys
import tempfile

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from local_run import persist_sli_trend_snapshot


def build_report(mode, sent, errors, attemptable, attempted, delivery_rate, failure_rate):
    return {
        "mode": mode,
        "dry_run": True,
        "summary": {
            "reminder_sent_count": sent,
            "reminder_send_error_count": errors,
            "reminder_delivery_attemptable_count": attemptable,
            "reminder_delivery_attempted_count": attempted,
            "reminder_delivery_rate": delivery_rate,
            "reminder_failure_rate": failure_rate,
        },
    }


def run():
    with tempfile.TemporaryDirectory() as tmp_dir:
        trend_file = Path(tmp_dir) / "sli_trend.json"
        count = persist_sli_trend_snapshot(
            build_report("reminders-only", 1, 0, 1, 1, 1.0, 0.0),
            trend_file,
            limit=2,
        )
        assert count == 1, count

        count = persist_sli_trend_snapshot(
            build_report("reminders-only", 2, 1, 3, 3, 0.6667, 0.3333),
            trend_file,
            limit=2,
        )
        assert count == 2, count

        count = persist_sli_trend_snapshot(
            build_report("sync-only", 0, 0, 0, 0, None, None),
            trend_file,
            limit=2,
        )
        assert count == 2, count

        snapshots = json.loads(trend_file.read_text(encoding="utf-8"))
        assert len(snapshots) == 2, snapshots
        assert snapshots[0]["mode"] == "reminders-only", snapshots
        assert snapshots[1]["mode"] == "sync-only", snapshots
        assert snapshots[0]["reminder_delivery_rate"] == 0.6667, snapshots
        assert snapshots[1]["reminder_delivery_rate"] is None, snapshots
        assert all("captured_at_utc" in snapshot for snapshot in snapshots), snapshots
    print("reminder_sli_trend_persistence_smoke_ok")


if __name__ == "__main__":
    run()

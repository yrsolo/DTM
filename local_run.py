"""Local launcher for running the planner without Yandex Cloud."""

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from main import main


def build_event(trigger_id):
    """Build minimal event payload compatible with cloud handler contract."""
    return {
        "messages": [
            {
                "details": {
                    "trigger_id": trigger_id,
                }
            }
        ]
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Run planner locally")
    parser.add_argument(
        "--mode",
        choices=("timer", "morning", "test", "sync-only", "reminders-only"),
        help="Direct mode override (recommended for local runs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Disable Google Sheets write operations (read-only verification run).",
    )
    parser.add_argument(
        "--event-file",
        type=Path,
        help="Path to Yandex event JSON file (optional).",
    )
    parser.add_argument(
        "--trigger-id",
        help="Synthetic trigger_id for event emulation.",
    )
    parser.add_argument(
        "--quality-report-file",
        type=Path,
        help="Optional path to write quality report JSON.",
    )
    parser.add_argument(
        "--sli-trend-file",
        type=Path,
        help="Optional path to persist rolling reminder SLI snapshots across runs.",
    )
    parser.add_argument(
        "--sli-trend-limit",
        type=int,
        default=200,
        help="Max number of snapshots to keep in --sli-trend-file (default: 200).",
    )
    parser.add_argument(
        "--mock-external",
        action="store_true",
        help="Disable OpenAI and Telegram external calls in reminder flow.",
    )
    return parser.parse_args()


def _build_sli_trend_snapshot(quality_report):
    report = dict(quality_report or {})
    summary = dict(report.get("summary", {}))
    return {
        "captured_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": report.get("mode"),
        "dry_run": bool(report.get("dry_run", False)),
        "reminder_delivery_attemptable_count": summary.get("reminder_delivery_attemptable_count"),
        "reminder_delivery_attempted_count": summary.get("reminder_delivery_attempted_count"),
        "reminder_delivery_rate": summary.get("reminder_delivery_rate"),
        "reminder_failure_rate": summary.get("reminder_failure_rate"),
        "reminder_sent_count": summary.get("reminder_sent_count"),
        "reminder_send_error_count": summary.get("reminder_send_error_count"),
    }


def persist_sli_trend_snapshot(quality_report, trend_file, limit=200):
    if limit <= 0:
        raise ValueError("sli-trend-limit must be a positive integer")

    trend_file = Path(trend_file)
    trend_file.parent.mkdir(parents=True, exist_ok=True)
    snapshots = []

    if trend_file.exists():
        try:
            raw = json.loads(trend_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raw = []
        if isinstance(raw, list):
            snapshots = raw

    snapshots.append(_build_sli_trend_snapshot(quality_report))
    snapshots = snapshots[-limit:]
    trend_file.write_text(
        json.dumps(snapshots, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(snapshots)


def load_event(args):
    if args.event_file:
        return json.loads(args.event_file.read_text(encoding="utf-8"))
    if args.trigger_id:
        return build_event(args.trigger_id)
    return None


if __name__ == "__main__":
    args = parse_args()
    event = load_event(args)
    quality_report = asyncio.run(
        main(
            mode=args.mode,
            event=event,
            dry_run=args.dry_run,
            mock_external=args.mock_external,
        )
    )
    if args.quality_report_file:
        args.quality_report_file.parent.mkdir(parents=True, exist_ok=True)
        args.quality_report_file.write_text(
            json.dumps(quality_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"quality_report_file={args.quality_report_file}")
    if args.sli_trend_file:
        snapshot_count = persist_sli_trend_snapshot(
            quality_report=quality_report,
            trend_file=args.sli_trend_file,
            limit=args.sli_trend_limit,
        )
        print(f"sli_trend_file={args.sli_trend_file} snapshots={snapshot_count}")

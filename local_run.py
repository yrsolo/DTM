"""Local launcher for running the planner without Yandex Cloud."""

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from agent.reminder_alert_evaluator import (
    evaluate_thresholds,
    maybe_notify_owner,
    resolve_fail_on,
    should_fail,
)
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
    parser.add_argument(
        "--evaluate-alerts",
        action="store_true",
        help="Evaluate reminder alert thresholds from current quality report.",
    )
    parser.add_argument(
        "--alert-evaluation-file",
        type=Path,
        help="Optional path to write alert evaluation JSON.",
    )
    parser.add_argument(
        "--alert-fail-profile",
        choices=("local", "ci"),
        default="local",
        help="Alert exit profile preset: local=none, ci=warn (default: local).",
    )
    parser.add_argument(
        "--alert-fail-on",
        choices=("none", "warn", "critical"),
        default=None,
        help="Explicit alert exit severity override (default: use --alert-fail-profile).",
    )
    parser.add_argument(
        "--notify-owner-on",
        choices=("none", "warn", "critical"),
        default="none",
        help="Trigger owner-notify helper from alert evaluation (default: none).",
    )
    parser.add_argument(
        "--notify-owner-context",
        default="",
        help="Optional context for owner notify helper (Russian text).",
    )
    parser.add_argument(
        "--notify-owner-dry-run",
        action="store_true",
        help="Print owner notify command without sending Telegram message.",
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


def build_alert_evaluation(quality_report):
    return evaluate_thresholds(quality_report=quality_report)


def persist_alert_evaluation(alert_evaluation, out_file):
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(alert_evaluation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_event(args):
    if args.event_file:
        return json.loads(args.event_file.read_text(encoding="utf-8"))
    if args.trigger_id:
        return build_event(args.trigger_id)
    return None


def _default_notify_context(mode: str | None) -> str:
    run_mode = mode or "авторежим"
    return f"локальный запуск: режим {run_mode}"


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
    alert_evaluation = None
    effective_fail_on = resolve_fail_on(args.alert_fail_profile, args.alert_fail_on)
    should_eval_alerts = (
        args.evaluate_alerts
        or args.alert_evaluation_file
        or args.notify_owner_on != "none"
        or args.alert_fail_profile != "local"
        or args.alert_fail_on is not None
    )
    if should_eval_alerts:
        alert_evaluation = build_alert_evaluation(quality_report)
        print(
            "alert_eval "
            f"level={alert_evaluation['level']} "
            f"attemptable={alert_evaluation['summary']['reminder_delivery_attemptable_count']} "
            f"delivery_rate={alert_evaluation['summary']['reminder_delivery_rate']} "
            f"send_errors={alert_evaluation['summary']['reminder_send_error_count']}"
        )
        print(f"alert_reason={alert_evaluation['reason']}")
        print(
            "alert_fail_policy "
            f"profile={args.alert_fail_profile} effective_fail_on={effective_fail_on}"
        )
        maybe_notify_owner(
            alert_evaluation=alert_evaluation,
            notify_on=args.notify_owner_on,
            notify_context=args.notify_owner_context or _default_notify_context(args.mode),
            notify_dry_run=args.notify_owner_dry_run,
        )
    if args.alert_evaluation_file and alert_evaluation is not None:
        persist_alert_evaluation(alert_evaluation, args.alert_evaluation_file)
        print(f"alert_evaluation_file={args.alert_evaluation_file}")
    if alert_evaluation is not None and should_fail(alert_evaluation["level"], effective_fail_on):
        raise SystemExit(2)

"""Evaluate reminder alert level from quality report artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate reminder alert thresholds from quality_report artifacts."
    )
    parser.add_argument(
        "--quality-report-file",
        type=Path,
        help="Optional explicit quality_report.json path.",
    )
    parser.add_argument(
        "--search-root",
        type=Path,
        default=Path("artifacts") / "baseline",
        help="Root directory to search for latest quality_report.json (default: artifacts/baseline).",
    )
    parser.add_argument(
        "--warn-delivery-rate",
        type=float,
        default=0.98,
        help="WARN threshold for reminder_delivery_rate.",
    )
    parser.add_argument(
        "--critical-delivery-rate",
        type=float,
        default=0.95,
        help="CRITICAL threshold for reminder_delivery_rate.",
    )
    parser.add_argument(
        "--critical-send-errors",
        type=int,
        default=3,
        help="CRITICAL threshold for reminder_send_error_count.",
    )
    parser.add_argument(
        "--min-sample-size",
        type=int,
        default=5,
        help="Minimum attemptable count required for WARN/CRITICAL evaluation.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "warn", "critical"),
        default="critical",
        help="Exit non-zero when level meets/exceeds configured severity.",
    )
    return parser.parse_args()


def find_latest_quality_report(search_root: Path) -> Path:
    candidates = list(search_root.rglob("quality_report.json"))
    if not candidates:
        raise FileNotFoundError(f"No quality_report.json found under: {search_root}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def evaluate_thresholds(
    quality_report: dict[str, Any],
    min_sample_size: int = 5,
    warn_delivery_rate: float = 0.98,
    critical_delivery_rate: float = 0.95,
    critical_send_errors: int = 3,
) -> dict[str, Any]:
    summary = dict(quality_report.get("summary", {}))
    attemptable = int(summary.get("reminder_delivery_attemptable_count") or 0)
    delivery_rate = summary.get("reminder_delivery_rate")
    send_errors = int(summary.get("reminder_send_error_count") or 0)
    source_mode = quality_report.get("mode")

    level = "OK"
    reason = "Thresholds are within acceptable range."

    if attemptable < min_sample_size:
        level = "INFO_ONLY"
        reason = (
            f"Insufficient sample size: attemptable={attemptable} < min_sample_size={min_sample_size}."
        )
    else:
        if (delivery_rate is not None and float(delivery_rate) < critical_delivery_rate) or (
            send_errors >= critical_send_errors
        ):
            level = "CRITICAL"
            reason = (
                "Critical threshold breached: "
                f"delivery_rate={delivery_rate}, send_errors={send_errors}."
            )
        elif delivery_rate is not None and float(delivery_rate) < warn_delivery_rate:
            level = "WARN"
            reason = f"Warning threshold breached: delivery_rate={delivery_rate}."

    return {
        "level": level,
        "reason": reason,
        "mode": source_mode,
        "summary": {
            "reminder_delivery_attemptable_count": attemptable,
            "reminder_delivery_rate": delivery_rate,
            "reminder_send_error_count": send_errors,
        },
        "thresholds": {
            "min_sample_size": min_sample_size,
            "warn_delivery_rate": warn_delivery_rate,
            "critical_delivery_rate": critical_delivery_rate,
            "critical_send_errors": critical_send_errors,
        },
    }


def should_fail(level: str, fail_on: str) -> bool:
    if fail_on == "none":
        return False
    if fail_on == "critical":
        return level == "CRITICAL"
    return level in {"WARN", "CRITICAL"}


def main() -> int:
    args = parse_args()
    source_file = args.quality_report_file or find_latest_quality_report(args.search_root)
    quality_report = json.loads(source_file.read_text(encoding="utf-8"))
    result = evaluate_thresholds(
        quality_report=quality_report,
        min_sample_size=args.min_sample_size,
        warn_delivery_rate=args.warn_delivery_rate,
        critical_delivery_rate=args.critical_delivery_rate,
        critical_send_errors=args.critical_send_errors,
    )
    result["source_file"] = str(source_file)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            "alert_eval "
            f"level={result['level']} "
            f"attemptable={result['summary']['reminder_delivery_attemptable_count']} "
            f"delivery_rate={result['summary']['reminder_delivery_rate']} "
            f"send_errors={result['summary']['reminder_send_error_count']} "
            f"source={source_file}"
        )
        print(f"reason={result['reason']}")

    return 2 if should_fail(result["level"], args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())

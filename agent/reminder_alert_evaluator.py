"""Evaluate reminder alert level from quality report artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


FAIL_PROFILES = {
    "local": "none",
    "ci": "warn",
}

LEVEL_RU = {
    "CRITICAL": "критический",
    "WARN": "предупреждение",
    "INFO_ONLY": "информационный",
    "OK": "норма",
    "UNKNOWN": "неизвестно",
}


def _summary_value(summary: dict[str, Any], key: str, cast: type, default: Any) -> Any:
    value = summary.get(key, default)
    try:
        return cast(value)
    except (TypeError, ValueError):
        return default


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
        "--fail-profile",
        choices=tuple(FAIL_PROFILES.keys()),
        default="ci",
        help="Exit profile preset: local=none, ci=warn (default: ci).",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "warn", "critical"),
        default=None,
        help="Explicit severity gate override (default: use --fail-profile preset).",
    )
    parser.add_argument(
        "--notify-owner-on",
        choices=("none", "warn", "critical"),
        default="none",
        help="Trigger owner notify helper when level meets/exceeds severity (default: none).",
    )
    parser.add_argument(
        "--notify-owner-context",
        default="",
        help="Optional context passed to owner notify helper (Russian text).",
    )
    parser.add_argument(
        "--notify-owner-dry-run",
        action="store_true",
        help="Print notify command without sending Telegram message.",
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
    attemptable = _summary_value(summary, "reminder_delivery_attemptable_count", int, 0)
    delivery_rate = summary.get("reminder_delivery_rate")
    send_errors = _summary_value(summary, "reminder_send_error_count", int, 0)
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


def resolve_fail_on(fail_profile: str, fail_on_override: str | None) -> str:
    if fail_on_override is not None:
        return fail_on_override
    return FAIL_PROFILES.get(fail_profile, "none")


def should_notify(level: str, notify_on: str) -> bool:
    if notify_on == "none":
        return False
    if notify_on == "critical":
        return level == "CRITICAL"
    return level in {"WARN", "CRITICAL"}


def _build_notify_payload(alert_evaluation: dict[str, Any], context: str = "") -> dict[str, str]:
    level = str(alert_evaluation.get("level", "UNKNOWN"))
    summary = dict(alert_evaluation.get("summary", {}))
    attemptable = summary.get("reminder_delivery_attemptable_count")
    delivery_rate = summary.get("reminder_delivery_rate")
    send_errors = summary.get("reminder_send_error_count")
    level_ru = LEVEL_RU.get(level, LEVEL_RU["UNKNOWN"])

    if level == "CRITICAL":
        title = "🚨 Критический уровень: напоминания"
        reason_ru = "Превышен критический порог качества отправки."
    elif level == "WARN":
        title = "❓ Предупреждение: напоминания"
        reason_ru = "Достигнут предупреждающий порог качества отправки."
    elif level == "INFO_ONLY":
        title = "✅ Информация: напоминания"
        reason_ru = "Недостаточно данных для строгой оценки."
    else:
        title = "✅ Норма: напоминания"
        reason_ru = "Показатели в допустимых границах."

    details = (
        f"Уровень: {level_ru}. Проверяемых отправок: {attemptable}. "
        f"Доля доставок: {delivery_rate}. Ошибок отправки: {send_errors}. "
        f"Причина: {reason_ru}."
    )
    options = (
        "1) создать новый чат для инцидента и задачи исправления; "
        "2) ответить тимлиду и продолжить текущий чат с выбранным вариантом"
    )
    return {
        "title": title,
        "details": details,
        "options": options,
        "context": context or f"оценка оповещения: уровень {level_ru}",
    }


def maybe_notify_owner(
    alert_evaluation: dict[str, Any],
    notify_on: str = "none",
    notify_context: str = "",
    notify_dry_run: bool = False,
) -> bool:
    level = str(alert_evaluation.get("level", "UNKNOWN"))
    if not should_notify(level, notify_on):
        return False

    payload = _build_notify_payload(alert_evaluation, context=notify_context)
    cmd = [
        sys.executable,
        "agent/notify_owner.py",
        "--mode",
        "info",
        "--title",
        payload["title"],
        "--details",
        payload["details"],
        "--options",
        payload["options"],
        "--context",
        payload["context"],
    ]
    if notify_dry_run:
        print("owner_notify_dry_run command=" + json.dumps(cmd, ensure_ascii=False))
        return True

    run = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if run.returncode != 0:
        stdout = (run.stdout or "").strip()
        stderr = (run.stderr or "").strip()
        raise RuntimeError(
            f"owner_notify_failed rc={run.returncode} stdout={stdout} stderr={stderr}"
        )
    print(f"owner_notify_sent level={level}")
    return True


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

    maybe_notify_owner(
        alert_evaluation=result,
        notify_on=args.notify_owner_on,
        notify_context=args.notify_owner_context,
        notify_dry_run=args.notify_owner_dry_run,
    )

    effective_fail_on = resolve_fail_on(args.fail_profile, args.fail_on)
    print(f"alert_fail_policy profile={args.fail_profile} effective_fail_on={effective_fail_on}")
    return 2 if should_fail(result["level"], effective_fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())

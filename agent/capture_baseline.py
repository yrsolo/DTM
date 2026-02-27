"""Capture repeatable baseline artifacts for Stage 0.4 validation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_python(repo: Path) -> str:
    venv_python = repo / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _run(cmd: Sequence[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )


def _safe_label(label: str) -> str:
    keep = []
    for ch in label.strip():
        if ch.isalnum() or ch in {"-", "_"}:
            keep.append(ch)
        else:
            keep.append("_")
    cleaned = "".join(keep).strip("_")
    return cleaned or "baseline"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture baseline validation artifacts")
    parser.add_argument(
        "--label",
        default="baseline",
        help="Optional artifact label suffix (letters/numbers/-/_).",
    )
    parser.add_argument(
        "--python",
        dest="python_bin",
        help="Optional python executable path for local_run.py.",
    )
    parser.add_argument(
        "--mode",
        default="sync-only",
        choices=("sync-only", "timer", "test"),
        help="Run mode for capture (default: sync-only).",
    )
    parser.add_argument(
        "--alert-fail-profile",
        choices=("local", "ci"),
        default="local",
        help="Alert exit profile passed to local_run (default: local).",
    )
    parser.add_argument(
        "--alert-fail-on",
        choices=("none", "warn", "critical"),
        help="Optional explicit alert exit severity override passed to local_run.",
    )
    parser.add_argument(
        "--notify-owner-on",
        choices=("none", "warn", "critical"),
        default="none",
        help="Optional owner-notify severity gate for alert evaluation (default: none).",
    )
    parser.add_argument(
        "--notify-owner-dry-run",
        action="store_true",
        help="Print notify command without sending Telegram message.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = _repo_root()
    python_bin = args.python_bin or _default_python(repo)

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%d_%H%M%SZ")
    label = _safe_label(args.label)
    out_dir = repo / "artifacts" / "baseline" / f"{stamp}_{label}"
    out_dir.mkdir(parents=True, exist_ok=True)

    quality_report_file = out_dir / "quality_report.json"
    alert_evaluation_file = out_dir / "alert_evaluation.json"
    cmd = [
        python_bin,
        "local_run.py",
        "--mode",
        args.mode,
        "--dry-run",
        "--evaluate-alerts",
        "--alert-fail-profile",
        args.alert_fail_profile,
        "--alert-evaluation-file",
        str(alert_evaluation_file),
        "--quality-report-file",
        str(quality_report_file),
    ]
    if args.alert_fail_on is not None:
        cmd.extend(["--alert-fail-on", args.alert_fail_on])
    if args.notify_owner_on != "none":
        cmd.extend(
            [
                "--notify-owner-on",
                args.notify_owner_on,
                "--notify-owner-context",
                f"baseline_capture label={label}",
            ]
        )
    if args.notify_owner_dry_run:
        cmd.append("--notify-owner-dry-run")
    run = _run(cmd, repo)

    (out_dir / "sync_dry_run.log").write_text(
        (run.stdout or "") + ("\n[stderr]\n" + run.stderr if run.stderr else ""),
        encoding="utf-8",
    )

    git_sha = _run(["git", "rev-parse", "--short", "HEAD"], repo)
    meta = {
        "captured_at_utc": now.isoformat(),
        "cwd": str(repo),
        "command": cmd,
        "exit_code": run.returncode,
        "git_sha": (git_sha.stdout or "").strip(),
        "notes": [
            "dry-run mode is expected to avoid Google Sheets write requests",
            "compare this bundle with previous baseline bundle for regressions",
            "quality_report.json contains structured Stage 1 diagnostics snapshot",
        ],
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    checklist = """# Baseline Validation Checklist

- [ ] Dry-run command exited with code 0.
- [ ] Log contains `[DRY-RUN] GoogleSheetsService::execute_updates` entries only (no real writes).
- [ ] quality_report.json exists and summary counts look expected.
- [ ] alert_evaluation.json exists and contains level/reason fields.
- [ ] Retry taxonomy summary fields are present (`reminder_send_retry_attempt_count`, `reminder_send_retry_exhausted_count`, `reminder_send_error_transient_count`, `reminder_send_error_permanent_count`, `reminder_send_error_unknown_count`).
- [ ] If `reminder_send_error_unknown_count > 0`, create follow-up taxonomy task and link it in Jira evidence.
- [ ] Compare row/column counts in target sheets against previous baseline.
- [ ] Compare key milestone cells against previous baseline.
- [ ] Compare presence of notes/colors in sampled cells.
- [ ] Record outcome in agile task work log and Jira comment.
"""
    (out_dir / "CHECKLIST.md").write_text(checklist, encoding="utf-8")

    print(f"artifact_dir={out_dir}")
    print(f"exit_code={run.returncode}")
    return run.returncode


if __name__ == "__main__":
    raise SystemExit(main())

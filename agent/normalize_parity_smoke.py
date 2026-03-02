"""Parity smoke between legacy-style timing parse and new normalize path.

This smoke is intentionally narrow:
- compares only planned stage dates on controlled fixtures
- does not require full legacy runtime bootstrap
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.models.contracts import TaskRaw
from src.core.normalize.interface import normalize_task

DATE_AT_LINE_START = re.compile(r"^(\d{2}\.\d{2})\s+(.*)$")


def _legacy_like_parse_dates(raw_timing: str, anchor: date) -> list[str]:
    dates: list[date] = []
    for line in (raw_timing or "").splitlines():
        line = line.strip()
        match = DATE_AT_LINE_START.match(line)
        if not match:
            continue
        token = match.group(1)
        day = int(token[:2])
        month = int(token[3:])
        year = anchor.year
        candidate = date(year=year, month=month, day=day)
        if dates and candidate < dates[-1]:
            candidate = date(year=year + 1, month=month, day=day)
        dates.append(candidate)
    return [d.isoformat() for d in dates]


def _new_normalize_dates(stages_raw: str, anchor: date) -> list[str]:
    task = TaskRaw(
        source_file_id="smoke",
        source_sheet_name="TASKS",
        source_row_id="1",
        title_raw="Smoke",
        stages_raw=stages_raw,
    )
    normalized = normalize_task(task, anchor_date=anchor)
    result: list[str] = []
    for stage in normalized.stages:
        if stage.planned_at is not None:
            result.append(stage.planned_at.isoformat())
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run normalize parity smoke")
    parser.add_argument("--anchor-date", default="2026-12-30", help="Anchor date YYYY-MM-DD")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    anchor = date.fromisoformat(args.anchor_date)

    fixtures = [
        {
            "name": "simple_two_stages",
            "legacy_raw_timing": "05.03 Черновик\n08.03 Финал",
            "new_stages_raw": "Черновик 05.03; Финал 08.03",
        },
        {
            "name": "year_boundary",
            "legacy_raw_timing": "31.12 Концепт\n02.01 Финал",
            "new_stages_raw": "Концепт 31.12; Финал 02.01",
        },
    ]

    report: list[dict[str, object]] = []
    failed = False
    for fixture in fixtures:
        legacy_dates = _legacy_like_parse_dates(fixture["legacy_raw_timing"], anchor=anchor)
        new_dates = _new_normalize_dates(fixture["new_stages_raw"], anchor=anchor)
        ok = legacy_dates == new_dates
        report.append(
            {
                "name": fixture["name"],
                "legacy_dates": legacy_dates,
                "new_dates": new_dates,
                "ok": ok,
            }
        )
        if not ok:
            failed = True

    print(json.dumps({"artifact": "normalize_parity_smoke", "report": report}, ensure_ascii=False, indent=2))
    if failed:
        print("normalize_parity_smoke_failed")
        return 1
    print("normalize_parity_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


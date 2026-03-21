"""Timing parser extracted from repository for domain-level reuse."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import pandas as pd

from src.core.contracts import is_nullish, normalize_text
from src.core.errors import TimingParseIssue


def _is_nullish(value: Any) -> bool:
    return is_nullish(value)


def _normalize_text(value: Any, strip: bool = True) -> str:
    return normalize_text(value, strip=strip)


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("ascii", "replace").decode("ascii"))


class TimingParser:
    """Parse raw timing text into date -> stages mapping."""

    def __init__(self, timing_year_mode: str | None = None) -> None:
        self.legacy_date_pattern = re.compile(r"(\d{2}\.\d{2})")
        self.date_with_year_pattern = re.compile(r"^(\d{2}\.\d{2}\.\d{4})")
        self.date_with_short_year_pattern = re.compile(r"^(\d{2}\.\d{2}\.\d{2})(?!\d)")
        self.date_pattern = re.compile(r"^(\d{2}\.\d{2})(?!\.\d{2,4})")
        self.parse_issues: list[TimingParseIssue] = []
        self.total_parse_errors = 0
        self.timing_year_mode = str(timing_year_mode or "legacy").lower()
        self.year_resolution_events: list[dict[str, Any]] = []

    def reset_diagnostics(self) -> None:
        self.parse_issues = []
        self.total_parse_errors = 0
        self.year_resolution_events = []

    def issues_since(self, start_index: int) -> list[TimingParseIssue]:
        if start_index < 0:
            start_index = 0
        return self.parse_issues[start_index:]

    def parse(
        self,
        timing_str: str,
        next_task_date: pd.Timestamp | None = None,
        row_number: int = 0,
    ) -> dict[pd.Timestamp, list[str]]:
        if self.timing_year_mode == "legacy":
            return self._parse_legacy(
                timing_str=timing_str,
                next_task_date=next_task_date,
                row_number=row_number,
            )
        return self._parse_with_anchors(
            timing_str=timing_str,
            next_task_date=next_task_date,
            row_number=row_number,
        )

    def _parse_legacy(
        self,
        timing_str: str,
        next_task_date: pd.Timestamp | None = None,
        row_number: int = 0,
    ) -> dict[pd.Timestamp, list[str]]:
        if next_task_date is None:
            next_task_date = pd.Timestamp.now()
        else:
            next_task_date = pd.Timestamp(next_task_date)
        timings: dict[pd.Timestamp, list[str]] = {}

        if _is_nullish(timing_str):
            return timings
        timing_str = str(timing_str)
        if not timing_str.strip():
            return timings
        lines = timing_str.strip().split("\n")

        for line in lines:
            line = line.strip()
            match = self.legacy_date_pattern.match(line)
            if not match:
                continue

            date_str = match.group(1)
            stage = line[len(date_str) :].strip().strip("-").strip()
            if not stage:
                continue
            year = next_task_date.year
            month = date_str[3:]
            day = date_str[:2]
            formatted_date_str = f"{year}-{month}-{day}"
            try:
                date = pd.Timestamp(formatted_date_str)
            except ValueError as exc:
                if month == "02" and day == "29":
                    continue
                err_text = (
                    "Timing parse error: "
                    f"{formatted_date_str} line={line} details={exc}"
                )
                _safe_print(err_text)
                issue = TimingParseIssue(
                    row_number=row_number,
                    timing_line=line,
                    normalized_date=formatted_date_str,
                    error=str(exc),
                )
                self.parse_issues.append(issue)
                self.total_parse_errors += 1
                date = pd.Timestamp.now()

            if date < (next_task_date - pd.DateOffset(months=5)):
                date = date + pd.DateOffset(years=1)
            elif date > (next_task_date + pd.DateOffset(months=5)):
                date = date - pd.DateOffset(years=1)
            timings.setdefault(date, []).append(stage)

        return timings

    def _parse_with_anchors(
        self,
        timing_str: str,
        next_task_date: pd.Timestamp | None = None,
        row_number: int = 0,
    ) -> dict[pd.Timestamp, list[str]]:
        if next_task_date is None:
            next_task_date = pd.Timestamp.now()
        else:
            next_task_date = pd.Timestamp(next_task_date)
        timings: dict[pd.Timestamp, list[str]] = {}

        if _is_nullish(timing_str):
            return timings
        timing_str = str(timing_str)
        if not timing_str.strip():
            return timings
        lines = timing_str.strip().split("\n")

        for raw_line in lines:
            line = raw_line.strip()
            token, source = self._extract_date_token(line)
            if not token:
                continue
            stage = line[len(token) :].strip().strip("-").strip()
            if not stage:
                continue
            date = self._resolve_timing_date(
                token=token,
                source=source,
                next_task_date=next_task_date,
                line=line,
                row_number=row_number,
            )
            if date is None:
                continue
            timings.setdefault(date, []).append(stage)
            self.year_resolution_events.append(
                {
                    "row_number": row_number,
                    "timing_line": line,
                    "normalized_date": date.strftime("%Y-%m-%d"),
                    "year_source": source,
                    "confidence": "high" if source == "explicit_anchor" else "medium",
                }
            )

        return timings

    def _extract_date_token(self, line: str) -> tuple[str, str]:
        match = self.date_with_year_pattern.match(line)
        if match:
            return match.group(1), "explicit_anchor"
        match = self.date_with_short_year_pattern.match(line)
        if match:
            return match.group(1), "explicit_anchor"
        match = self.date_pattern.match(line)
        if match:
            return match.group(1), "legacy_next_task"
        return "", ""

    def _resolve_timing_date(
        self,
        *,
        token: str,
        source: str,
        next_task_date: pd.Timestamp,
        line: str,
        row_number: int,
    ) -> pd.Timestamp | None:
        try:
            if source == "explicit_anchor":
                if len(token) == 10:
                    return pd.Timestamp(datetime.strptime(token, "%d.%m.%Y")).normalize()
                return pd.Timestamp(datetime.strptime(token, "%d.%m.%y")).normalize()
            year = next_task_date.year
            month = token[3:]
            day = token[:2]
            date = pd.Timestamp(f"{year}-{month}-{day}")
        except ValueError as exc:
            if token.startswith("29.02"):
                return None
            issue = TimingParseIssue(
                row_number=row_number,
                timing_line=line,
                normalized_date=token,
                error=str(exc),
            )
            self.parse_issues.append(issue)
            self.total_parse_errors += 1
            return None

        if date < (next_task_date - pd.DateOffset(months=5)):
            return (date + pd.DateOffset(years=1)).normalize()
        if date > (next_task_date + pd.DateOffset(months=5)):
            return (date - pd.DateOffset(years=1)).normalize()
        return date.normalize()


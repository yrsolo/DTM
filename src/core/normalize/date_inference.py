"""Date inference helpers (e.g. dd.mm without year)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class DateInferenceResult:
    """Result of date inference from ambiguous textual source."""

    value: date | None
    confidence: float
    rule: str


def infer_date(value: str, anchor: date, prev: date | None = None) -> DateInferenceResult:
    """Infer date from textual input.

    Current M1 skeleton:
    - supports `dd.mm`
    - infers year by anchor
    - bumps year when monotonic sequence would otherwise go backwards from `prev`
    """
    text = (value or "").strip()
    if not text:
        return DateInferenceResult(value=None, confidence=0.0, rule="empty")

    parts = text.split(".")
    if len(parts) < 2:
        return DateInferenceResult(value=None, confidence=0.0, rule="unparsed")

    try:
        day = int(parts[0])
        month = int(parts[1])
    except ValueError:
        return DateInferenceResult(value=None, confidence=0.0, rule="unparsed")

    year = anchor.year
    try:
        inferred = date(year=year, month=month, day=day)
    except ValueError:
        return DateInferenceResult(value=None, confidence=0.0, rule="invalid_date")

    rule = "dd.mm->year_by_anchor"
    confidence = 0.8
    if prev and inferred < prev:
        try:
            inferred = date(year=year + 1, month=month, day=day)
            rule = "dd.mm->year_by_anchor_plus_one"
            confidence = 0.7
        except ValueError:
            return DateInferenceResult(value=None, confidence=0.0, rule="invalid_date")

    return DateInferenceResult(value=inferred, confidence=confidence, rule=rule)


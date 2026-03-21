"""Domain task model."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.core.contracts import normalize_text
from src.core.timing_parser import TimingParser


def _normalize(value: Any, strip: bool = True) -> str:
    return normalize_text(value, strip=strip)


class Task:
    def __init__(
        self,
        brand: Any,
        format_: Any,
        project_name: Any,
        customer: Any,
        designer: Any,
        raw_timing: Any,
        status: Any,
        color: Any,
        color_status: Any,
        name: Any,
        task_id: Any,
        parser: TimingParser | None = None,
        next_task_date: pd.Timestamp | None = None,
        source_row_number: int = 0,
    ) -> None:
        self.brand = _normalize(brand)
        self.format_ = _normalize(format_)
        self.project_name = _normalize(project_name)
        self.customer = _normalize(customer)
        self.designer = _normalize(designer)
        self.raw_timing = _normalize(raw_timing, strip=False)
        self.timing_cache = None
        self.status = _normalize(status)
        self.color = color
        self.color_status = _normalize(color_status)
        self.name = _normalize(name)
        self.id = task_id
        self.parser = parser or TimingParser()
        self.next_task_date = next_task_date
        self.source_row_number = int(source_row_number or 0)

    def __repr__(self) -> str:
        return f"{self.id} {self.name}"

    @property
    def timing(self) -> dict[pd.Timestamp, list[str]]:
        if self.timing_cache:
            return self.timing_cache
        self.timing_cache = self.parser.parse(
            self.raw_timing,
            self.next_task_date,
            row_number=self.source_row_number,
        )
        return self.timing_cache

    @property
    def max_date(self) -> pd.Timestamp | None:
        return max(self.timing.keys()) if self.timing else None

    @property
    def min_date(self) -> pd.Timestamp | None:
        return min(self.timing.keys()) if self.timing else None

    @property
    def max(self):
        return self.max_date

    @property
    def min(self):
        return self.min_date


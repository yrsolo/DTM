"""Domain timing processor for task calendar structures."""

from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from core.timing_parser import TimingParser


def get_date_range(timings_dict: dict[pd.Timestamp, list[str]]) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return min/max date for parsed timing dictionary."""
    min_date = min(timings_dict.keys())
    max_date = max(timings_dict.keys())
    return min_date, max_date


class TaskTimingProcessor:
    """Build normalized timing payload for calendar managers."""

    def __init__(self, timing_year_mode: str | None = None) -> None:
        self.timing_year_mode = timing_year_mode

    def create_task_timing_structure(self, tasks: Iterable[Any]) -> dict[str, Any]:
        """Convert tasks into normalized timing structure with global date bounds."""
        global_min_date = pd.Timestamp.max
        global_max_date = pd.Timestamp.min

        task_structure = []
        parser = TimingParser(timing_year_mode=self.timing_year_mode)
        for task in tasks:
            timings_dict = parser.parse(task.raw_timing)
            if not timings_dict:
                continue
            min_date, max_date = get_date_range(timings_dict)
            global_min_date = min(global_min_date, min_date)
            global_max_date = max(global_max_date, max_date)
            timings_list = [{"date": date, "stage": stage} for date, stage in timings_dict.items()]
            task_structure.append(
                {
                    "id": task.id,
                    "name": task.name,
                    "designer": task.designer,
                    "customer": task.customer,
                    "status": task.status,
                    "color_status": task.color_status,
                    "timings": timings_list,
                    "min_date": min_date,
                    "max_date": max_date,
                }
            )
        return {"timings": task_structure, "min_date": global_min_date, "max_date": global_max_date}

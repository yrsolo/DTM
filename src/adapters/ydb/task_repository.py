"""Task-repository adapter backed by normalized YDB operational tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.adapters.ydb.operational_repo import OperationalTaskRepo


class _TimingDiagnostics:
    def __init__(self) -> None:
        self.parse_issues: list[str] = []
        self.total_parse_errors: int = 0


def _to_timestamp(value: Any) -> pd.Timestamp | None:
    if value is None:
        return None
    if isinstance(value, int):
        # YDB `Date` may be returned as day-offset from Unix epoch.
        if 0 <= value <= 200_000:
            return (pd.Timestamp("1970-01-01") + pd.to_timedelta(value, unit="D")).normalize()
    try:
        ts = pd.Timestamp(value)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    return ts.normalize()


@dataclass
class YdbTaskView:
    id: str
    name: str
    designer: str
    status: str
    color_status: str
    brand: str
    format_: str
    project_name: str
    customer: str
    raw_timing: str
    timing: dict[pd.Timestamp, list[str]]

    @property
    def min_date(self) -> pd.Timestamp | None:
        return min(self.timing.keys()) if self.timing else None

    @property
    def max_date(self) -> pd.Timestamp | None:
        return max(self.timing.keys()) if self.timing else None

    @property
    def next_due(self) -> pd.Timestamp | None:
        today = pd.Timestamp.today().normalize()
        future = [value for value in self.timing.keys() if value >= today]
        return min(future) if future else self.max_date


class YdbOperationalTaskRepository:
    """Repository interface expected by planner/renderer/reminder layers."""

    def __init__(
        self,
        *,
        endpoint: str,
        database: str,
        sa_json_credentials: str | None = None,
        sa_key_file: str | None = None,
        repo: OperationalTaskRepo | None = None,
    ) -> None:
        self.repo = repo or OperationalTaskRepo(
            endpoint=endpoint,
            database=database,
            sa_json_credentials=sa_json_credentials,
            sa_key_file=sa_key_file,
            ensure_schema=False,
        )
        self.row_issues: list[str] = []
        self.timing_parser = _TimingDiagnostics()
        self._cache_all: list[YdbTaskView] | None = None

    def _build_tasks(self, *, statuses: list[str] | None = None) -> list[YdbTaskView]:
        task_rows = self.repo.list_tasks(statuses=statuses)
        task_ids = [str(row.get("task_id", "")).strip() for row in task_rows if str(row.get("task_id", "")).strip()]
        milestone_rows = self.repo.list_milestones(task_ids=task_ids, include_details=False)
        milestones_by_task: dict[str, list[dict[str, Any]]] = {}
        for row in milestone_rows:
            task_id = str(row.get("task_id", "")).strip()
            if not task_id:
                continue
            milestones_by_task.setdefault(task_id, []).append(row)
        for rows in milestones_by_task.values():
            rows.sort(key=lambda item: int(item.get("idx", 0) or 0))

        tasks: list[YdbTaskView] = []
        for row in task_rows:
            task_id = str(row.get("task_id", "")).strip()
            if not task_id:
                continue
            timing: dict[pd.Timestamp, list[str]] = {}
            for item in milestones_by_task.get(task_id, []):
                planned_ts = _to_timestamp(item.get("planned_date"))
                if planned_ts is None:
                    self.timing_parser.total_parse_errors += 1
                    self.timing_parser.parse_issues.append(f"task_id={task_id} milestone_missing_planned_date")
                    continue
                stage_type = str(item.get("type", "")).strip() or "unknown"
                timing.setdefault(planned_ts, []).append(stage_type)
            tasks.append(
                YdbTaskView(
                    id=task_id,
                    name=str(row.get("title", "")).strip(),
                    designer=str(row.get("owner_id", "")).strip(),
                    status=str(row.get("status", "")).strip(),
                    color_status=str(row.get("status", "")).strip().lower() or "work",
                    brand=str(row.get("brand", "")).strip(),
                    format_=str(row.get("format_", "")).strip(),
                    project_name=str(row.get("group_id", "")).strip(),
                    customer=str(row.get("customer", "")).strip(),
                    raw_timing=str(row.get("raw_timing", "")).strip(),
                    timing=timing,
                )
            )
        return tasks

    def get_all_tasks(self) -> list[YdbTaskView]:
        if self._cache_all is None:
            self._cache_all = self._build_tasks(statuses=list(self.ACTIVE_STATUSES))
        return list(self._cache_all)

    def get_task_by_color_status(self, color_status: Any) -> list[YdbTaskView]:
        values = color_status if isinstance(color_status, (list, tuple, set)) else [color_status]
        statuses = [str(item).strip().lower() for item in values if str(item).strip()]
        return self._build_tasks(statuses=statuses)

    def get_tasks_by_date(self, date: pd.Timestamp) -> list[YdbTaskView]:
        day = pd.Timestamp(date).normalize()
        tasks = self.get_task_by_color_status(["work"])
        return [task for task in tasks if day in task.timing]
    ACTIVE_STATUSES = ("wait", "work", "pre_done")

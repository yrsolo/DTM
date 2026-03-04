"""Google Sheets task repository adapter."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Mapping

import pandas as pd

from core.contracts import TaskRowContract, is_nullish
from core.errors import MissingRequiredColumnsError, RowValidationIssue
from core.models.task import Task
from core.task_repository_contract import TaskRepository
from core.timing_parser import TimingParser
from src.config.loader import load_config

if TYPE_CHECKING:
    from utils.service import GoogleSheetInfo, GoogleSheetsService


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("ascii", "replace").decode("ascii"))


def _determine_status_from_color(color: Any, color_status_map: Mapping[str, str]) -> str:
    try:
        color_status = color_status_map.get(color, "work")
    except Exception:
        print("error in convert color: ", color, "\n set it to WORK")
        color_status = "work"
    return color_status


class GoogleSheetsTaskRepository(TaskRepository):
    """Google Sheets backed repository for task data."""

    def __init__(
        self,
        sheet_info: GoogleSheetInfo,
        service: GoogleSheetsService,
        source_sheet_info: GoogleSheetInfo | None = None,
        timing_year_mode: str | None = None,
        task_field_map: Mapping[str, str] | None = None,
        replace_names: Mapping[str, str] | None = None,
        color_status_map: Mapping[str, str] | None = None,
    ) -> None:
        cfg = load_config()
        self.sheet_info = sheet_info
        self.source_sheet_info = source_sheet_info or sheet_info
        self.service = service
        self.df = None
        self.task_field_map = dict(task_field_map or cfg.tables.field_maps.get("tasks", {}))
        self.replace_names = dict(replace_names or cfg.mapping.project_aliases)
        self.color_status_map = dict(color_status_map or cfg.mapping.status_by_color)
        self.tasks = dict()
        self.row_issues: list[RowValidationIssue] = []
        self.timing_parser = TimingParser(timing_year_mode=timing_year_mode)
        self.dop = {}

    def get_all_tasks(self) -> list[Task]:
        self._load()
        return [task for task in self.tasks.values()]

    def get_tasks_by_date(self, date: pd.Timestamp) -> list[Task]:
        self._load()
        tasks = self.get_task_by_color_status(["work"])
        return [task for task in tasks if date in task.timing.keys()]

    def get_task_by(self, column_name: str, value: Any) -> list[Task] | Task:
        ids = self._filter(column_name, value)["id"]
        return self.get_task_by_id(ids)

    def get_task_by_id(self, task_ids: Any) -> list[Task] | Task:
        self._load()
        if isinstance(task_ids, Iterable):
            return [self.tasks[task_id] for task_id in task_ids]
        return self.tasks[task_ids]

    def get_task_by_color_status(self, color_status: Any) -> list[Task] | Task:
        return self.get_task_by("color_status", color_status)

    def _load_and_process_data(self) -> None:
        spreadsheet_name = self.source_sheet_info.spreadsheet_name
        sheet_name = self.source_sheet_info.get_sheet_name("tasks")
        assistant_sheet_name = self.source_sheet_info.get_sheet_name("assistant")
        df = self.service.get_dataframe(spreadsheet_name, sheet_name)
        self._validate_required_columns(df, spreadsheet_name, sheet_name)
        color_range = f"A2:A{len(df) + 1}"
        colors = self.service.get_cell_colors(spreadsheet_name, sheet_name, color_range)
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].fillna("")
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].apply(
            lambda x: "\n".join(sorted([item.strip() for item in x.split("\n") if item.strip()]))
        )
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].apply(lambda x: "[Не назначен]" if x == "" else x)
        df["color"] = colors
        df["color_status"] = df["color"].apply(
            lambda color: _determine_status_from_color(color, self.color_status_map)
        )
        df["id"] = df.index + 2
        df["name"] = df.apply(self._generate_task_name, axis=1)

        self.dop = {
            "assiatant_main_prompt": self.service.get_dataframe(
                spreadsheet_name, assistant_sheet_name, worksheet_range="F3:F4", header=False
            ).at[0, 0],
            "assistant_model": self.service.get_dataframe(
                spreadsheet_name, assistant_sheet_name, worksheet_range="E3:E4", header=False
            ).at[0, 0],
            "assistant_advice": self.service.get_dataframe(
                spreadsheet_name, assistant_sheet_name, worksheet_range="B3:B1000", header=False
            ),
        }

        self.df = df
        self._df_to_task(df)

    def _validate_required_columns(self, df: pd.DataFrame, spreadsheet_name: str, sheet_name: str) -> None:
        required_columns = TaskRowContract.required_columns(self.task_field_map)
        missing = sorted(col for col in required_columns if col not in df.columns)
        if missing:
            raise MissingRequiredColumnsError(
                entity_name="task",
                spreadsheet_name=spreadsheet_name,
                sheet_name=sheet_name,
                missing_columns=tuple(missing),
                field_map_name="TASK_FIELD_MAP",
            )

    def _generate_task_name(self, row: pd.Series) -> str:
        raw_format = row.get("ФОРМАТ", "")
        raw_format = "" if pd.isna(raw_format) else str(raw_format)
        format_ = raw_format.split("\n")[0] if raw_format else ""
        brand = "" if pd.isna(row.get("БРЕНД")) else str(row.get("БРЕНД"))
        project = "" if pd.isna(row.get("ПРОЕКТ")) else str(row.get("ПРОЕКТ"))
        name = f"{brand} [{project}] {format_}".strip()
        for key, value in self.replace_names.items():
            name = name.replace(key, value)
        return name

    def _load(self) -> None:
        if self.df is None:
            self._load_and_process_data()

    def _df_to_task(self, df: pd.DataFrame) -> list[Task]:
        self.row_issues = []
        self.tasks = dict()
        self.timing_parser.reset_diagnostics()
        tasks_list = []
        next_task_date = None
        for idx, row in df.iterrows():
            row_number = int(idx) + 2
            try:
                contract = TaskRowContract.from_mapping(row, self.task_field_map)
                task = Task(
                    **contract.to_task_kwargs(),
                    parser=self.timing_parser,
                    next_task_date=next_task_date,
                    source_row_number=row_number,
                )
            except (TypeError, ValueError, KeyError) as exc:
                self._record_row_issue("task", row_number, f"mapping failure: {exc}")
                continue
            if is_nullish(task.id):
                self._record_row_issue("task", row_number, "missing task id")
                continue
            if task.id in self.tasks:
                self._record_row_issue("task", row_number, "duplicate task id", row_id=str(task.id))
                continue
            tasks_list.append(task)
            self.tasks[task.id] = task
            issue_cursor = len(self.timing_parser.parse_issues)
            task_dates = sorted(task.timing.keys())
            if self.timing_parser.timing_year_mode == "chain":
                task_dates = self._apply_chain_year_shift(task, task_dates, next_task_date)
            pivot_date = None
            if task_dates:
                if self.timing_parser.timing_year_mode == "legacy":
                    pivot_date = pd.Series(task_dates).mean()
                else:
                    pivot_date = pd.Series(task_dates).median()
            new_issues = self.timing_parser.issues_since(issue_cursor)
            if new_issues:
                self._record_row_issue(
                    "task",
                    row_number,
                    f"timing parse errors: {len(new_issues)}",
                    row_id=str(task.id),
                )
            if pivot_date is not None and not pd.isna(pivot_date):
                next_task_date = pd.Timestamp(pivot_date)
        return tasks_list

    def _apply_chain_year_shift(
        self,
        task: Task,
        task_dates: list[pd.Timestamp],
        previous_task_date: pd.Timestamp | None,
    ) -> list[pd.Timestamp]:
        if not task_dates or previous_task_date is None:
            return task_dates
        previous_task_date = pd.Timestamp(previous_task_date).normalize()
        future_threshold = previous_task_date + pd.Timedelta(days=21)
        future_jan_mar = [date for date in task_dates if date > future_threshold and date.month in {1, 2, 3}]
        mostly_jan_mar = len([date for date in task_dates if date.month in {1, 2, 3}]) >= max(1, len(task_dates) // 2)
        all_after_previous = all(date > previous_task_date for date in task_dates)
        force_q4_rollover = previous_task_date.month >= 10 and mostly_jan_mar and all_after_previous
        if not force_q4_rollover and len(future_jan_mar) < max(1, len(task_dates) // 2):
            return task_dates

        shifted_dates = [
            (date - pd.DateOffset(years=1)).normalize() if date.month in {1, 2, 3} else date
            for date in task_dates
        ]
        original_gap = sum(abs((date - previous_task_date).days) for date in task_dates)
        shifted_gap = sum(abs((date - previous_task_date).days) for date in shifted_dates)
        if not force_q4_rollover and shifted_gap + 14 >= original_gap:
            return task_dates

        timing_map = task.timing
        shifted_map = defaultdict(list)
        for old_date, new_date in zip(task_dates, shifted_dates):
            shifted_map[new_date].extend(timing_map.get(old_date, []))
        task.timing_cache = dict(shifted_map)
        shifted_sorted = sorted(task.timing_cache.keys())
        self.timing_parser.year_resolution_events.append(
            {
                "row_number": task.source_row_number,
                "timing_line": task.raw_timing.split("\n")[0] if task.raw_timing else "",
                "normalized_date": shifted_sorted[0].strftime("%Y-%m-%d") if shifted_sorted else "",
                "year_source": "chain_shift",
                "confidence": "medium",
            }
        )
        return shifted_sorted

    def _record_row_issue(self, entity_name: str, row_number: int, reason: str, row_id: str = "") -> None:
        issue = RowValidationIssue(
            entity_name=entity_name,
            row_number=row_number,
            reason=reason,
            row_id=row_id,
        )
        self.row_issues.append(issue)
        _safe_print(str(issue))

    def _filter(self, column_name: str, value: Any) -> pd.DataFrame:
        self._load()
        if not isinstance(value, Iterable):
            value = [value]
        return self.df[self.df[column_name].isin(value)]

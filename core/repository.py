"""Task repositories and timing parser for Google Sheets source data."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime
from typing import Any

import pandas as pd

from config import COLOR_STATUS, REPLACE_NAMES, TASK_FIELD_MAP, TIMING_YEAR_MODE
from core.contracts import TaskRowContract, is_nullish, normalize_text
from core.errors import MissingRequiredColumnsError, RowValidationIssue, TimingParseIssue
from core.reminder import TelegramNotifier
from utils.service import GoogleSheetInfo, GoogleSheetsService


def _is_nullish(value: Any) -> bool:
    """Compatibility wrapper for local module usage."""
    return is_nullish(value)


def _normalize_text(value: Any, strip: bool = True) -> str:
    """Compatibility wrapper for local module usage."""
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
        self.logger = TelegramNotifier()
        self.parse_issues: list[TimingParseIssue] = []
        self.total_parse_errors = 0
        self.timing_year_mode = (timing_year_mode or TIMING_YEAR_MODE).lower()
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
        """Convert timing multiline text to normalized dictionary."""
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
        """Original parser behavior preserved for regression-safe mode."""
        if next_task_date is None:
            next_task_date = pd.Timestamp.now()
        else:
            next_task_date = pd.Timestamp(next_task_date)
        timings = defaultdict(list)

        # Разбиваем строку на отдельные строки по переносам.
        if _is_nullish(timing_str):
            return timings
        timing_str = str(timing_str)
        if not timing_str.strip():
            return timings
        lines = timing_str.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Ищем дату в начале строки
            match = self.legacy_date_pattern.match(line)
            if not match:
                continue

            date_str = match.group(1)
            stage = line[len(date_str) :].strip().strip("-").strip()
            if stage:
                # Преобразуем строку даты в объект pandas.Timestamp
                # year = datetime.datetime.now().year
                year = next_task_date.year
                month = date_str[3:]
                day = date_str[:2]
                formatted_date_str = f"{year}-{month}-{day}"
                try:
                    # Попытка преобразования даты
                    date = pd.Timestamp(formatted_date_str)
                except ValueError as e:
                    if month == "02" and day == "29":
                        continue
                    # Обработка ошибки и вывод строки, которую не удалось преобразовать
                    err_text = f"""Ошибка преобразования даты: {formatted_date_str}
Строка тайминга: {line}
Подробности ошибки: {e}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
                    _safe_print(err_text)
                    if month != "02" or day != "29":
                        _safe_print("Timing parse Telegram log skipped in sync context")
                    issue = TimingParseIssue(
                        row_number=row_number,
                        timing_line=line,
                        normalized_date=formatted_date_str,
                        error=str(e),
                    )
                    self.parse_issues.append(issue)
                    self.total_parse_errors += 1
                    date = pd.Timestamp.now()

                if date < (next_task_date - pd.DateOffset(months=5)):
                    date = date + pd.DateOffset(years=1)
                elif date > (next_task_date + pd.DateOffset(months=5)):
                    date = date - pd.DateOffset(years=1)
                timings[date].append(stage)

        return dict(timings)

    def _parse_with_anchors(
        self,
        timing_str: str,
        next_task_date: pd.Timestamp | None = None,
        row_number: int = 0,
    ) -> dict[pd.Timestamp, list[str]]:
        """Enhanced parser with explicit-year anchors plus legacy fallback rules."""
        if next_task_date is None:
            next_task_date = pd.Timestamp.now()
        else:
            next_task_date = pd.Timestamp(next_task_date)
        timings = defaultdict(list)

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
            timings[date].append(stage)
            self.year_resolution_events.append(
                {
                    "row_number": row_number,
                    "timing_line": line,
                    "normalized_date": date.strftime("%Y-%m-%d"),
                    "year_source": source,
                    "confidence": "high" if source == "explicit_anchor" else "medium",
                }
            )

        return dict(timings)

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
        self.brand = _normalize_text(brand)
        self.format_ = _normalize_text(format_)
        self.project_name = _normalize_text(project_name)
        self.customer = _normalize_text(customer)
        self.designer = _normalize_text(designer)
        self.raw_timing = _normalize_text(raw_timing, strip=False)
        self.timing_cache = None
        self.status = _normalize_text(status)
        self.color = color
        self.color_status = _normalize_text(color_status)
        self.name = _normalize_text(name)
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
        else:
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


# 2. Репозитории
# Определим интерфейсы и базовую реализацию:


class TaskRepository(ABC):
    """Base task repository contract."""

    @abstractmethod
    def get_all_tasks(self) -> list[Task]:
        raise NotImplementedError


def _determine_status_from_color(color: Any) -> str:
    """Resolve task status from color mapping."""
    cs = COLOR_STATUS
    try:
        color_status = cs.get(color, "work")
    except:
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
    ) -> None:
        # sheet_info is used as target for writes by managers.
        self.sheet_info = sheet_info
        # source_sheet_info is used for reads from main table.
        self.source_sheet_info = source_sheet_info or sheet_info
        self.service = service
        self.df = None
        self.replace_names = REPLACE_NAMES
        self.tasks = dict()
        self.row_issues: list[RowValidationIssue] = []
        self.timing_parser = TimingParser()
        self.dop = {}

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks from current sheet snapshot."""
        self._load()
        return [task for task in self.tasks.values()]

    def get_tasks_by_date(self, date: pd.Timestamp) -> list[Task]:
        """Return active work tasks that contain given date in timing."""
        self._load()
        tasks = self.get_task_by_color_status(["work"])
        return [task for task in tasks if date in task.timing.keys()]

    def get_task_by(self, column_name: str, value: Any) -> list[Task] | Task:
        """Return tasks filtered by dataframe column value."""
        ids = self._filter(column_name, value)["id"]
        return self.get_task_by_id(ids)

    def get_task_by_id(self, task_ids: Any) -> list[Task] | Task:
        """Return task or list of tasks by id(s)."""
        self._load()
        if isinstance(task_ids, Iterable):
            return [self.tasks[task_id] for task_id in task_ids]
        else:
            return self.tasks[task_ids]

    def get_task_by_color_status(self, color_status: Any) -> list[Task] | Task:
        """Return tasks filtered by color status."""
        return self.get_task_by("color_status", color_status)

    def _load_and_process_data(self) -> None:
        """Load task dataframe and convert to in-memory task objects."""
        spreadsheet_name = self.source_sheet_info.spreadsheet_name
        sheet_name = self.source_sheet_info.get_sheet_name("tasks")
        assistant_sheet_name = self.source_sheet_info.get_sheet_name("assistant")
        df = self.service.get_dataframe(spreadsheet_name, sheet_name)
        self._validate_required_columns(df, spreadsheet_name, sheet_name)
        color_range = f"A2:A{len(df) + 1}"
        colors = self.service.get_cell_colors(spreadsheet_name, sheet_name, color_range)
        # в ячейке ДИЗАЙНЕР может быть несколько человек, там str в котором на каждой строчке один человек
        # надо эти строчки отсортировать по алфавиту удалив лишние пробелы в начале и конце каждоый строки
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].fillna("")
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].apply(
            lambda x: "\n".join(sorted([i.strip() for i in x.split("\n") if i.strip()]))
        )
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].apply(lambda x: "[Не назначен]" if x == "" else x)
        df["color"] = colors
        df["color_status"] = df["color"].apply(_determine_status_from_color)
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
        required_columns = TaskRowContract.required_columns(TASK_FIELD_MAP)
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
        """Generate human-readable task name from row fields."""
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
        """Load dataframe once and keep snapshot for repository methods."""
        if self.df is None:
            self._load_and_process_data()

    def _df_to_task(self, df: pd.DataFrame) -> list[Task]:
        """Convert dataframe rows into Task objects with diagnostics."""
        self.row_issues = []
        self.tasks = dict()
        self.timing_parser.reset_diagnostics()
        tasks_list = []
        next_task_date = None
        for idx, row in df.iterrows():
            row_number = int(idx) + 2
            try:
                contract = TaskRowContract.from_mapping(row, TASK_FIELD_MAP)
                task = Task(
                    **contract.to_task_kwargs(),
                    parser=self.timing_parser,
                    next_task_date=next_task_date,
                    source_row_number=row_number,
                )
            except (TypeError, ValueError, KeyError) as exc:
                self._record_row_issue("task", row_number, f"mapping failure: {exc}")
                continue
            if _is_nullish(task.id):
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
        """Apply guarded year-shift for Jan-Mar future jumps in chain mode."""
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
        """Filter source dataframe by value(s) of selected column."""
        self._load()
        # если не кортеж или список, то преобразуем в список
        if not isinstance(value, Iterable):
            value = [value]
        return self.df[self.df[column_name].isin(value)]

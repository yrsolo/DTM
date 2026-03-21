"""Row-based Sheets task normalization for active snapshot runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd

from src.core.contracts import TaskRowContract, is_nullish
from src.core.errors import MissingRequiredColumnsError, RowValidationIssue
from src.core.models.task import Task
from src.core.timing_parser import TimingParser


def normalize_designer_cell(value: Any) -> str:
    if is_nullish(value):
        return ""
    designers = [str(item).strip() for item in str(value).split("\n") if str(item).strip()]
    return "\n".join(sorted(designers))


def build_row_mappings(worksheet_values: list[list[Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    if not worksheet_values:
        return [], []
    raw_columns = [str(item or "").strip() for item in list(worksheet_values[0] or [])]
    data_rows = [list(row or []) for row in worksheet_values[1:]]
    if not data_rows:
        return raw_columns, []

    target_width = max(len(raw_columns), max((len(row) for row in data_rows), default=0))
    columns = list(raw_columns)
    if len(columns) < target_width:
        for index in range(len(columns), target_width):
            columns.append(f"__extra_col_{index + 1}")
    else:
        columns = columns[:target_width]

    rows: list[dict[str, Any]] = []
    for row in data_rows:
        normalized_row = list(row[:target_width])
        if len(normalized_row) < target_width:
            normalized_row.extend([""] * (target_width - len(normalized_row)))
        rows.append(dict(zip(columns, normalized_row)))
    return columns, rows


def validate_required_columns(
    columns: list[str],
    *,
    field_map: Mapping[str, str],
    spreadsheet_name: str,
    sheet_name: str,
) -> None:
    required_columns = TaskRowContract.required_columns(field_map)
    missing = sorted(column for column in required_columns if column not in set(columns))
    if missing:
        raise MissingRequiredColumnsError(
            entity_name="task",
            spreadsheet_name=spreadsheet_name,
            sheet_name=sheet_name,
            missing_columns=tuple(missing),
            field_map_name="TASK_FIELD_MAP",
        )


def generate_task_name(row: Mapping[str, Any], replace_names: Mapping[str, str]) -> str:
    raw_format = "" if is_nullish(row.get("ФОРМАТ")) else str(row.get("ФОРМАТ"))
    format_ = raw_format.split("\n")[0] if raw_format else ""
    brand = "" if is_nullish(row.get("БРЕНД")) else str(row.get("БРЕНД"))
    project = "" if is_nullish(row.get("ПРОЕКТ")) else str(row.get("ПРОЕКТ"))
    name = f"{brand} [{project}] {format_}".strip()
    for key, value in dict(replace_names).items():
        name = name.replace(key, value)
    return name


@dataclass(frozen=True)
class TaskBuildResult:
    tasks: list[Task]
    row_issues: list[RowValidationIssue]


def build_tasks_from_rows(
    rows: list[dict[str, Any]],
    *,
    field_map: Mapping[str, str],
    replace_names: Mapping[str, str],
    color_status_map: Mapping[str, str],
    status_colors: list[Any],
    timing_parser: TimingParser,
) -> TaskBuildResult:
    row_issues: list[RowValidationIssue] = []
    tasks: list[Task] = []
    seen_ids: set[str] = set()
    next_task_date = None
    timing_parser.reset_diagnostics()

    for index, row in enumerate(rows):
        row_number = index + 2
        designer_column = str(field_map.get("designer", ""))
        if designer_column:
            designer_value = normalize_designer_cell(row.get(designer_column))
            row[designer_column] = designer_value or "[Не назначен]"

        color_value = status_colors[index] if index < len(status_colors) else ""
        row[str(field_map.get("color", "color"))] = color_value
        row[str(field_map.get("color_status", "color_status"))] = str(
            color_status_map.get(color_value, "work")
        )
        row[str(field_map.get("name", "name"))] = generate_task_name(row, replace_names)

        try:
            contract = TaskRowContract.from_mapping(row, field_map)
            task = Task(
                **contract.to_task_kwargs(),
                parser=timing_parser,
                next_task_date=next_task_date,
                source_row_number=row_number,
            )
        except (TypeError, ValueError, KeyError) as exc:
            row_issues.append(
                RowValidationIssue(
                    entity_name="task",
                    row_number=row_number,
                    reason=f"mapping failure: {exc}",
                )
            )
            continue

        task_id = str(getattr(task, "id", "")).strip()
        if is_nullish(task.id) or not task_id:
            row_issues.append(RowValidationIssue(entity_name="task", row_number=row_number, reason="missing task id"))
            continue
        if task_id in seen_ids:
            row_issues.append(
                RowValidationIssue(entity_name="task", row_number=row_number, reason="duplicate task id", row_id=task_id)
            )
            continue
        seen_ids.add(task_id)
        tasks.append(task)

        issue_cursor = len(timing_parser.parse_issues)
        task_dates = sorted(task.timing.keys())
        if timing_parser.timing_year_mode == "chain":
            task_dates = apply_chain_year_shift(task, task_dates, next_task_date, timing_parser)
        pivot_date = None
        if task_dates:
            if timing_parser.timing_year_mode == "legacy":
                pivot_date = pd.Series(task_dates).mean()
            else:
                pivot_date = pd.Series(task_dates).median()
        new_issues = timing_parser.issues_since(issue_cursor)
        if new_issues:
            row_issues.append(
                RowValidationIssue(
                    entity_name="task",
                    row_number=row_number,
                    reason=f"timing parse errors: {len(new_issues)}",
                    row_id=task_id,
                )
            )
        if pivot_date is not None and not pd.isna(pivot_date):
            next_task_date = pd.Timestamp(pivot_date)

    return TaskBuildResult(tasks=tasks, row_issues=row_issues)


def apply_chain_year_shift(
    task: Task,
    task_dates: list[pd.Timestamp],
    previous_task_date: pd.Timestamp | None,
    timing_parser: TimingParser,
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
        (date - pd.DateOffset(years=1)).normalize() if date.month in {1, 2, 3} else date for date in task_dates
    ]
    original_gap = sum(abs((date - previous_task_date).days) for date in task_dates)
    shifted_gap = sum(abs((date - previous_task_date).days) for date in shifted_dates)
    if not force_q4_rollover and shifted_gap + 14 >= original_gap:
        return task_dates

    timing_map = task.timing
    shifted_map: dict[pd.Timestamp, list[str]] = {}
    for old_date, new_date in zip(task_dates, shifted_dates):
        shifted_map.setdefault(new_date, []).extend(timing_map.get(old_date, []))
    task.timing_cache = dict(shifted_map)
    shifted_sorted = sorted(task.timing_cache.keys())
    timing_parser.year_resolution_events.append(
        {
            "row_number": task.source_row_number,
            "timing_line": task.raw_timing.split("\n")[0] if task.raw_timing else "",
            "normalized_date": shifted_sorted[0].strftime("%Y-%m-%d") if shifted_sorted else "",
            "year_source": "chain_shift",
            "confidence": "medium",
        }
    )
    return shifted_sorted


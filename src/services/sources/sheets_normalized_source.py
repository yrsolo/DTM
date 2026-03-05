"""Google Sheets backed task source without planner coupling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd

from src.adapters.google_sheets.task_repository import GoogleSheetsTaskRepository


def _normalize_designer_cell(value: Any) -> str:
    if pd.isna(value):
        return ""
    designers = [str(item).strip() for item in str(value).split("\n") if str(item).strip()]
    return "\n".join(sorted(designers))


def _dataframe_from_worksheet_values(
    worksheet_values: list[list[str]],
    *,
    header: bool = True,
) -> pd.DataFrame:
    if not worksheet_values:
        return pd.DataFrame()
    if not header:
        return pd.DataFrame(worksheet_values)

    raw_columns = list(worksheet_values[0] or [])
    data_rows = [list(row or []) for row in worksheet_values[1:]]
    if not data_rows:
        return pd.DataFrame(columns=raw_columns)

    target_width = max(len(raw_columns), max((len(row) for row in data_rows), default=0))
    normalized_columns = list(raw_columns)
    if len(normalized_columns) < target_width:
        for idx in range(len(normalized_columns), target_width):
            normalized_columns.append(f"__extra_col_{idx + 1}")
    else:
        normalized_columns = normalized_columns[:target_width]

    normalized_rows: list[list[str]] = []
    for row in data_rows:
        if len(row) < target_width:
            row = row + [""] * (target_width - len(row))
        elif len(row) > target_width:
            row = row[:target_width]
        normalized_rows.append(row)

    return pd.DataFrame(normalized_rows, columns=normalized_columns)


@dataclass(frozen=True)
class SheetsNormalizedTaskSource:
    """Task source that normalizes tasks directly from Sheets snapshots."""

    task_repository: GoogleSheetsTaskRepository

    @property
    def source_id(self) -> str:
        info = self.task_repository.source_sheet_info
        return f"sheet:{info.spreadsheet_name}:{info.get_sheet_name('tasks')}:A1:Z2000"

    @property
    def source_sheet_name(self) -> str:
        return str(self.task_repository.source_sheet_info.spreadsheet_name)

    def read_snapshot(self, worksheet_range: str) -> dict[str, object]:
        info = self.task_repository.source_sheet_info
        sheet_name = str(info.get_sheet_name("tasks") or "")
        values = self.task_repository.service.get_worksheet_values(
            spreadsheet_name=info.spreadsheet_name,
            worksheet_name=sheet_name,
            worksheet_range=worksheet_range,
        )
        colors = self.task_repository.service.get_cell_colors(
            spreadsheet_name=info.spreadsheet_name,
            worksheet_name=sheet_name,
            worksheet_range=worksheet_range,
        )
        return {
            "range": worksheet_range,
            "values": values,
            "colors": colors,
        }

    def build_tasks_from_snapshot(self, full_snapshot: dict[str, object]) -> list[Any]:
        values = full_snapshot.get("values")
        if not isinstance(values, list) or not values:
            self.task_repository.df = pd.DataFrame()
            self.task_repository.tasks = {}
            self.task_repository.row_issues = []
            return []

        info = self.task_repository.source_sheet_info
        sheet_name = str(info.get_sheet_name("tasks") or "")
        df = _dataframe_from_worksheet_values(values, header=True)
        self.task_repository._validate_required_columns(df, info.spreadsheet_name, sheet_name)

        designer_col = str(self.task_repository.task_field_map.get("designer", "ДИЗАЙНЕР"))
        if designer_col in df.columns:
            df[designer_col] = df[designer_col].fillna("")
            df[designer_col] = df[designer_col].apply(_normalize_designer_cell)
            df[designer_col] = df[designer_col].apply(lambda text: "[Не назначен]" if text == "" else text)

        colors = full_snapshot.get("colors")
        normalized_colors: list[Any]
        if isinstance(colors, list):
            normalized_colors = list(colors)
        else:
            normalized_colors = []
        if len(normalized_colors) == len(df) + 1:
            normalized_colors = normalized_colors[1:]
        if len(normalized_colors) < len(df):
            normalized_colors = normalized_colors + [""] * (len(df) - len(normalized_colors))
        elif len(normalized_colors) > len(df):
            normalized_colors = normalized_colors[: len(df)]

        # Always fetch canonical row colors from column A. Wide-range snapshot
        # color payloads (A1:Z*) are lossy for status mapping in Google API.
        info = self.task_repository.source_sheet_info
        sheet_name = str(info.get_sheet_name("tasks") or "")
        color_range = f"A2:A{len(df) + 1}"
        canonical_colors = self.task_repository.service.get_cell_colors(
            spreadsheet_name=info.spreadsheet_name,
            worksheet_name=sheet_name,
            worksheet_range=color_range,
        )
        if isinstance(canonical_colors, list) and canonical_colors:
            normalized_colors = list(canonical_colors)
            if len(normalized_colors) < len(df):
                normalized_colors = normalized_colors + [""] * (len(df) - len(normalized_colors))
            elif len(normalized_colors) > len(df):
                normalized_colors = normalized_colors[: len(df)]

        df["color"] = normalized_colors
        df["color_status"] = df["color"].apply(
            lambda color: self.task_repository.color_status_map.get(color, "work")
        )
        df["name"] = df.apply(self.task_repository._generate_task_name, axis=1)

        self.task_repository.df = df
        return self.task_repository._df_to_task(df)


def build_sheets_normalized_task_source(
    *,
    key_json: str,
    sheet_info_data: Mapping[str, str],
    cfg: Any,
    dry_run: bool,
) -> SheetsNormalizedTaskSource:
    """Build Sheets task source directly from cfg + credentials (no planner)."""
    from utils.service import GoogleSheetInfo, GoogleSheetsService

    source_sheet_name = str(cfg.tables.google_sheets.get("source_sheet_name_default", "")).strip()
    source_sheet_info_data = {
        "spreadsheet_name": source_sheet_name,
        "sheet_names": dict(cfg.tables.sheet_names),
    }
    timing_year_mode = str(cfg.runtime.timing.year_mode_default or "legacy")
    task_field_map = dict(cfg.tables.field_maps.get("tasks", {}))
    color_status_map = dict(cfg.mapping.status_by_color)
    replace_names = dict(cfg.mapping.project_aliases)

    sheet_info = GoogleSheetInfo(**sheet_info_data)
    source_sheet_info = GoogleSheetInfo(**source_sheet_info_data)
    service = GoogleSheetsService(key_json, dry_run=dry_run)
    repo = GoogleSheetsTaskRepository(
        sheet_info=sheet_info,
        service=service,
        source_sheet_info=source_sheet_info,
        timing_year_mode=timing_year_mode,
        task_field_map=task_field_map,
        replace_names=replace_names,
        color_status_map=color_status_map,
    )
    return SheetsNormalizedTaskSource(task_repository=repo)

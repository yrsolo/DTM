"""Google Sheets backed task source without planner coupling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.adapters.google_sheets.task_repository import GoogleSheetsTaskRepository
from src.services.sources.sheets_task_rows import (
    build_row_mappings,
    build_tasks_from_rows,
    validate_required_columns,
)


def _normalize_status_colors(status_colors: Any, row_count: int) -> list[Any]:
    if isinstance(status_colors, list):
        normalized = list(status_colors)
    else:
        normalized = []
    if len(normalized) < row_count:
        normalized.extend([""] * (row_count - len(normalized)))
    elif len(normalized) > row_count:
        normalized = normalized[:row_count]
    return normalized


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
        status_colors = self.task_repository.service.get_cell_colors(
            spreadsheet_name=info.spreadsheet_name,
            worksheet_name=sheet_name,
            worksheet_range=f"A2:A{max(2, len(values or []))}",
        )
        return {
            "range": worksheet_range,
            "values": values,
            "colors": list(status_colors or []),
            "status_colors": list(status_colors or []),
        }

    def build_tasks_from_snapshot(self, full_snapshot: dict[str, object]) -> list[Any]:
        values = full_snapshot.get("values")
        if not isinstance(values, list) or not values:
            self.task_repository.df = None
            self.task_repository.tasks = {}
            self.task_repository.row_issues = []
            return []

        info = self.task_repository.source_sheet_info
        sheet_name = str(info.get_sheet_name("tasks") or "")
        columns, rows = build_row_mappings(values)
        validate_required_columns(
            columns,
            field_map=self.task_repository.task_field_map,
            spreadsheet_name=str(info.spreadsheet_name),
            sheet_name=sheet_name,
        )
        status_colors = _normalize_status_colors(
            full_snapshot.get("status_colors", full_snapshot.get("colors")),
            len(rows),
        )
        build_result = build_tasks_from_rows(
            rows,
            field_map=self.task_repository.task_field_map,
            replace_names=self.task_repository.replace_names,
            color_status_map=self.task_repository.color_status_map,
            status_colors=status_colors,
            timing_parser=self.task_repository.timing_parser,
        )
        self.task_repository.df = None
        self.task_repository.tasks = {str(task.id): task for task in build_result.tasks}
        self.task_repository.row_issues = list(build_result.row_issues)
        return build_result.tasks


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

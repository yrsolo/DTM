"""Source snapshot readers extracted from main entrypoint."""

from __future__ import annotations

from typing import Any


def read_source_range_values(source_task_repository: Any, *, worksheet_range: str) -> list[list[str]]:
    spreadsheet_name = source_task_repository.source_sheet_info.spreadsheet_name
    sheet_name = source_task_repository.source_sheet_info.get_sheet_name("tasks")
    return source_task_repository.service.get_worksheet_values(
        spreadsheet_name=spreadsheet_name,
        worksheet_name=sheet_name,
        worksheet_range=worksheet_range,
    )


def read_source_range_colors(source_task_repository: Any, *, worksheet_range: str) -> list[str]:
    spreadsheet_name = source_task_repository.source_sheet_info.spreadsheet_name
    sheet_name = source_task_repository.source_sheet_info.get_sheet_name("tasks")
    return source_task_repository.service.get_cell_colors(
        spreadsheet_name=spreadsheet_name,
        worksheet_name=sheet_name,
        worksheet_range=worksheet_range,
    )


def read_source_snapshot(source_task_repository: Any, *, worksheet_range: str) -> dict[str, object]:
    return {
        "range": worksheet_range,
        "values": read_source_range_values(source_task_repository, worksheet_range=worksheet_range),
        "colors": read_source_range_colors(source_task_repository, worksheet_range=worksheet_range),
    }

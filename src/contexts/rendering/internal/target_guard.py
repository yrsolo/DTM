from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderTarget:
    source_spreadsheet: str
    target_spreadsheet: str
    tasks_sheet_name: str
    target_worksheet: str


def validate_render_target(target: RenderTarget) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    tasks_sheet = str(target.tasks_sheet_name or "").strip().lower()
    worksheet = str(target.target_worksheet or "").strip().lower()
    source_book = str(target.source_spreadsheet or "").strip()
    target_book = str(target.target_spreadsheet or "").strip()
    if worksheet == tasks_sheet and tasks_sheet:
        warnings.append("target_worksheet_points_to_source_tasks_sheet")
    if source_book and target_book and source_book == target_book and worksheet == tasks_sheet and tasks_sheet:
        warnings.append("target_spreadsheet_equals_source_and_worksheet_is_tasks")
    return len(warnings) == 0, warnings

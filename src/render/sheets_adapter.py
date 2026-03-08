from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import RenderApplyResult, RenderPlan


class SheetsWriter:
    """Infra adapter that writes RenderPlan to Google Sheets in batches."""

    def apply(self, plan: RenderPlan) -> RenderApplyResult:
        raise NotImplementedError


@dataclass(frozen=True)
class SheetTarget:
    spreadsheet_name: str
    worksheet_name: str


class GoogleSheetsPlanWriter(SheetsWriter):
    """Batch apply `RenderPlan` values to target worksheet with one update request."""

    def __init__(self, service: Any, target: SheetTarget) -> None:
        self._service = service
        self._target = target

    def apply(self, plan: RenderPlan) -> RenderApplyResult:
        if not plan.values:
            return RenderApplyResult(
                applied=False,
                rows_written=0,
                cells_written=0,
                target_spreadsheet=self._target.spreadsheet_name,
                target_worksheet=self._target.worksheet_name,
                warnings=list(plan.warnings or ["empty_render_plan"]),
            )
        min_row = min(cell.row for cell in plan.values)
        max_row = max(cell.row for cell in plan.values)
        min_col = min(cell.col for cell in plan.values)
        max_col = max(cell.col for cell in plan.values)
        height = max_row - min_row + 1
        width = max_col - min_col + 1

        matrix: list[list[str]] = [["" for _ in range(width)] for _ in range(height)]
        for cell in plan.values:
            matrix[cell.row - min_row][cell.col - min_col] = str(cell.value or "")

        sheet_id = self._service.get_sheet_id_by_name(
            self._target.spreadsheet_name,
            self._target.worksheet_name,
        )
        if sheet_id is None:
            raise RuntimeError("render_sheet_not_found")

        rows_payload = []
        for row_values in matrix:
            rows_payload.append(
                {
                    "values": [
                        {"userEnteredValue": {"stringValue": value}}
                        for value in row_values
                    ]
                }
            )

        request = {
            "updateCells": {
                "rows": rows_payload,
                "fields": "userEnteredValue",
                "range": {
                    "sheetId": int(sheet_id),
                    "startRowIndex": min_row - 1,
                    "endRowIndex": max_row,
                    "startColumnIndex": min_col - 1,
                    "endColumnIndex": max_col,
                },
            }
        }
        self._service.execute_updates(self._target.spreadsheet_name, [request])
        return RenderApplyResult(
            applied=True,
            rows_written=height,
            cells_written=height * width,
            target_spreadsheet=self._target.spreadsheet_name,
            target_worksheet=self._target.worksheet_name,
            warnings=list(plan.warnings or []),
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import RenderApplyResult, RenderBorder, RenderCell, RenderPlan


class SheetsWriter:
    """Infra adapter that writes RenderPlan to Google Sheets in batches."""

    def apply(self, plan: RenderPlan) -> RenderApplyResult:
        raise NotImplementedError


@dataclass(frozen=True)
class SheetTarget:
    spreadsheet_name: str
    worksheet_name: str


class GoogleSheetsPlanWriter(SheetsWriter):
    """Apply RenderPlan via service queued requests and a single flush."""

    def __init__(self, service: Any, target: SheetTarget) -> None:
        self._service = service
        self._target = target

    def _to_cell_payload(self, cell: RenderCell) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "row": int(cell.row),
            "col": int(cell.col),
            "value": "" if cell.value is None else str(cell.value),
        }
        if cell.note is not None:
            payload["note"] = str(cell.note)
        if cell.color is not None:
            payload["color"] = str(cell.color)
        if cell.text_color is not None:
            payload["text_color"] = str(cell.text_color)
        if cell.bold is not None:
            payload["bold"] = bool(cell.bold)
        if cell.italic is not None:
            payload["italic"] = bool(cell.italic)
        if cell.font_size is not None:
            payload["font_size"] = int(cell.font_size)
        return payload

    def _to_border_payload(self, border: RenderBorder) -> dict[str, Any]:
        return {
            "worksheet_range": str(border.worksheet_range),
            "side": str(border.side),
            "width": int(border.width),
            "color": str(border.color),
        }

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

        self._service.set_spreadsheet_and_worksheet(
            self._target.spreadsheet_name,
            self._target.worksheet_name,
        )
        self._service.clear_cells(self._target.spreadsheet_name, self._target.worksheet_name)
        self._service.clear_requests()

        touched_rows: set[int] = set()
        for cell in plan.values:
            touched_rows.add(int(cell.row))
            self._service.update_cell(
                self._target.spreadsheet_name,
                self._target.worksheet_name,
                cell_data=self._to_cell_payload(cell),
            )

        for border in plan.borders:
            self._service.update_borders(
                self._target.spreadsheet_name,
                self._target.worksheet_name,
                border_data=self._to_border_payload(border),
            )

        self._service.execute_updates(self._target.spreadsheet_name)
        return RenderApplyResult(
            applied=True,
            rows_written=len(touched_rows),
            cells_written=len(plan.values),
            target_spreadsheet=self._target.spreadsheet_name,
            target_worksheet=self._target.worksheet_name,
            warnings=list(plan.warnings or []),
        )

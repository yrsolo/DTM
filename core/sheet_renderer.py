"""Sheet render adapter implementations."""

from __future__ import annotations

from typing import Any, Protocol

from core.adapters import SheetRenderAdapter


class _SheetService(Protocol):
    """Subset of service API required by sheet render adapter."""

    def set_spreadsheet_and_worksheet(self, spreadsheet_name: str, sheet_name: str) -> None:
        ...

    def clear_cells(self, spreadsheet_name: str, sheet_name: str, range_: str = "A1:ZZ1000") -> None:
        ...

    def clear_requests(self) -> None:
        ...

    def update_cell(self, spreadsheet_name: str, sheet_name: str, cell_data: dict[str, Any]) -> None:
        ...

    def update_borders(self, spreadsheet_name: str, sheet_name: str, border_data: dict[str, Any]) -> None:
        ...

    def execute_updates(self, spreadsheet_name: str) -> None:
        ...


class ServiceSheetRenderAdapter(SheetRenderAdapter):
    """Adapter that scopes render writes to a single spreadsheet/sheet pair."""

    def __init__(self, service: _SheetService, spreadsheet_name: str, sheet_name: str) -> None:
        self.service = service
        self.spreadsheet_name = spreadsheet_name
        self.sheet_name = sheet_name

    def begin(self) -> None:
        """Bind target spreadsheet and worksheet in service state."""
        self.service.set_spreadsheet_and_worksheet(self.spreadsheet_name, self.sheet_name)

    def clear_cells(self, range_: str = "A1:ZZ1000") -> None:
        """Queue clear operation for the selected sheet range."""
        self.service.clear_cells(self.spreadsheet_name, self.sheet_name, range_=range_)

    def clear_requests(self) -> None:
        """Drop pending batched update requests."""
        self.service.clear_requests()

    def update_cell(self, cell_data: dict[str, Any]) -> None:
        """Queue single cell update request."""
        self.service.update_cell(self.spreadsheet_name, self.sheet_name, cell_data=cell_data)

    def update_borders(self, border_data: dict[str, Any]) -> None:
        """Queue border update request."""
        self.service.update_borders(
            self.spreadsheet_name,
            self.sheet_name,
            border_data=border_data,
        )

    def execute_updates(self) -> None:
        """Flush all queued operations to the spreadsheet."""
        self.service.execute_updates(self.spreadsheet_name)

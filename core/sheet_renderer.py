"""Sheet render adapter implementations."""

from core.adapters import SheetRenderAdapter


class ServiceSheetRenderAdapter(SheetRenderAdapter):
    """Adapter that scopes render writes to a single spreadsheet/sheet pair."""

    def __init__(self, service, spreadsheet_name: str, sheet_name: str):
        self.service = service
        self.spreadsheet_name = spreadsheet_name
        self.sheet_name = sheet_name

    def begin(self) -> None:
        self.service.set_spreadsheet_and_worksheet(self.spreadsheet_name, self.sheet_name)

    def clear_cells(self, range_: str = "A1:ZZ1000") -> None:
        self.service.clear_cells(self.spreadsheet_name, self.sheet_name, range_=range_)

    def clear_requests(self) -> None:
        self.service.clear_requests()

    def update_cell(self, cell_data: dict) -> None:
        self.service.update_cell(self.spreadsheet_name, self.sheet_name, cell_data=cell_data)

    def update_borders(self, border_data: dict) -> None:
        self.service.update_borders(
            self.spreadsheet_name,
            self.sheet_name,
            border_data=border_data,
        )

    def execute_updates(self) -> None:
        self.service.execute_updates(self.spreadsheet_name)

"""Local smoke assertions for sheet render adapter call wiring."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.sheet_renderer import ServiceSheetRenderAdapter


class FakeService:
    def __init__(self):
        self.calls = []

    def set_spreadsheet_and_worksheet(self, spreadsheet_name, worksheet_name):
        self.calls.append(("set_spreadsheet_and_worksheet", spreadsheet_name, worksheet_name))

    def clear_cells(self, spreadsheet_name=None, sheet_name=None, range_="A1:ZZ1000"):
        self.calls.append(("clear_cells", spreadsheet_name, sheet_name, range_))

    def clear_requests(self):
        self.calls.append(("clear_requests",))

    def update_cell(self, spreadsheet_name=None, sheet_name=None, cell_data=None, **kwargs):
        self.calls.append(("update_cell", spreadsheet_name, sheet_name, cell_data, kwargs))

    def update_borders(self, spreadsheet_name=None, sheet_name=None, border_data=None, **kwargs):
        self.calls.append(("update_borders", spreadsheet_name, sheet_name, border_data, kwargs))

    def execute_updates(self, spreadsheet_name=None, requests=None):
        self.calls.append(("execute_updates", spreadsheet_name, requests))


def run():
    service = FakeService()
    adapter = ServiceSheetRenderAdapter(
        service=service,
        spreadsheet_name="sheet-A",
        sheet_name="calendar-A",
    )

    adapter.begin()
    adapter.clear_cells()
    adapter.clear_requests()
    adapter.update_cell({"row": 2, "col": 3, "value": "x"})
    adapter.update_borders({"worksheet_range": "A1:B2", "side": "left", "width": 1, "color": "gray"})
    adapter.execute_updates()

    assert service.calls[0] == ("set_spreadsheet_and_worksheet", "sheet-A", "calendar-A")
    assert service.calls[1] == ("clear_cells", "sheet-A", "calendar-A", "A1:ZZ1000")
    assert service.calls[2] == ("clear_requests",)
    assert service.calls[3][0] == "update_cell"
    assert service.calls[3][1] == "sheet-A"
    assert service.calls[3][2] == "calendar-A"
    assert service.calls[3][3]["row"] == 2
    assert service.calls[3][3]["col"] == 3
    assert service.calls[4][0] == "update_borders"
    assert service.calls[4][1] == "sheet-A"
    assert service.calls[4][2] == "calendar-A"
    assert service.calls[5] == ("execute_updates", "sheet-A", None)
    print("render_adapter_smoke_ok")


if __name__ == "__main__":
    run()

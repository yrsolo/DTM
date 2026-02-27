"""Local smoke assertions for adapter and manager render wiring."""

from pathlib import Path
import sys
from types import SimpleNamespace

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.manager import CalendarManager, TaskManager
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


class FakeRenderer:
    def __init__(self):
        self.calls = []
        self.cell_payloads = []

    def begin(self):
        self.calls.append("begin")

    def clear_cells(self, range_="A1:ZZ1000"):
        self.calls.append(f"clear_cells:{range_}")

    def clear_requests(self):
        self.calls.append("clear_requests")

    def update_cell(self, cell_data):
        self.calls.append("update_cell")
        self.cell_payloads.append(cell_data)

    def update_borders(self, border_data):
        self.calls.append("update_borders")

    def execute_updates(self):
        self.calls.append("execute_updates")


class FakeSheetInfo:
    def __init__(self):
        self.spreadsheet_name = "sheet-test"

    def get_sheet_name(self, kind):
        mapping = {
            "designers": "Designers",
            "calendar": "Calendar",
            "task_calendar": "Tasks",
        }
        return mapping[kind]


class FakeRepository:
    def __init__(self, tasks):
        self.tasks = tasks
        self.sheet_info = FakeSheetInfo()
        self.service = FakeService()

    def get_all_tasks(self):
        return list(self.tasks)


def run_adapter_contract_smoke():
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


def run_task_manager_adapter_smoke():
    tasks = [
        SimpleNamespace(
            id=1,
            name="Task A",
            designer="Alice",
            customer="Bob",
            status="work",
            color_status="work",
            raw_timing="01.01 этап",
        ),
        SimpleNamespace(
            id=2,
            name="Task B",
            designer="Alice",
            customer="Bob",
            status="work",
            color_status="pre_done",
            raw_timing="02.01 этап",
        ),
    ]
    repository = FakeRepository(tasks=tasks)
    renderer = FakeRenderer()
    manager = TaskManager(task_repository=repository, renderer=renderer)
    manager.task_to_table(color_status=("work", "pre_done"))

    assert renderer.calls[0] == "begin"
    assert renderer.calls[1].startswith("clear_cells")
    assert renderer.calls[-1] == "execute_updates"
    assert renderer.calls.count("update_cell") >= 4
    assert any(payload.get("value") == "Alice" for payload in renderer.cell_payloads)
    assert any(payload.get("value") == "Task A" for payload in renderer.cell_payloads)


def run_calendar_manager_adapter_smoke():
    repository = FakeRepository(tasks=[])
    renderer = FakeRenderer()
    manager = CalendarManager(
        sheet_info=repository.sheet_info,
        service=repository.service,
        repository=repository,
        renderer=renderer,
    )

    calendar = {
        pd.Timestamp("2026-02-25"): {"Alice": ["Task A [stage]"]},
        pd.Timestamp("2026-02-26"): {"Alice": ["Task B [stage]"]},
    }
    manager.write_calendar_to_sheet(calendar=calendar, min_date=None)

    assert renderer.calls[0] == "begin"
    assert renderer.calls[1].startswith("clear_cells")
    assert renderer.calls[-1] == "execute_updates"
    assert renderer.calls.count("update_cell") >= 5
    assert any(payload.get("value") == "Alice" for payload in renderer.cell_payloads)
    assert any(payload.get("value") == "25.02" for payload in renderer.cell_payloads)


def run():
    run_adapter_contract_smoke()
    run_task_manager_adapter_smoke()
    run_calendar_manager_adapter_smoke()
    print("render_adapter_smoke_ok")


if __name__ == "__main__":
    run()

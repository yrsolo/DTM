"""DEPRECATED: reference-only legacy task table rendering runtime service."""

from __future__ import annotations

from typing import Any, Sequence

import pandas as pd

from core.adapters import SheetRenderAdapter
from core.render_contracts import RenderCell
from core.sheet_renderer import ServiceSheetRenderAdapter
from core.task_query_contract import query_source_tasks
from utils.func import GetColor, cell_to_indices


class TaskManager:
    """Render grouped task list into the designers sheet."""

    def __init__(self, task_repository: Any, renderer: SheetRenderAdapter | None = None) -> None:
        self.repository = task_repository
        self.tasks: list[Any] = []
        self.designers: set[str] = set()
        self.get_color = GetColor()
        self.spreadsheet_name = self.repository.sheet_info.spreadsheet_name
        self.sheet_name = self.repository.sheet_info.get_sheet_name("designers")
        self.renderer = renderer or ServiceSheetRenderAdapter(
            service=self.repository.service,
            spreadsheet_name=self.spreadsheet_name,
            sheet_name=self.sheet_name,
        )

    def update(self) -> None:
        self.tasks = self.repository.get_all_tasks()
        self.designers = set(task.designer for task in self.tasks if task.designer)

    def task_to_table(self, color_status: Sequence[str] | str = ("work", "pre_done")) -> None:
        if color_status == "all":
            color_status = ["work", "pre_done", "done"]
        elif color_status == "done":
            color_status = ["pre_done", "done"]
        elif isinstance(color_status, str):
            color_status = [color_status]

        self.update()
        tasks = query_source_tasks(self.tasks, statuses=color_status, limit=10**9)
        self.renderer.begin()
        if self.sheet_name:
            self.renderer.clear_cells()

        start_row, col = 2, 2
        row = start_row + 1

        for designer in sorted(self.designers):
            tasks_for_designer = [task for task in tasks if task.designer == designer]
            if not tasks_for_designer:
                continue

            cell_data = self._build_designer_header_cell(designer=designer, row=start_row, col=col)
            self.renderer.update_cell(cell_data=cell_data)

            for task in tasks_for_designer:
                cell_data = self._build_task_cell(task=task, row=row, col=col)
                self.renderer.update_cell(cell_data=cell_data)
                row += 1

            col += 1
            row = start_row + 1

        self._write_cur_time(cell="A1")
        self.renderer.execute_updates()

    def _build_designer_header_cell(self, designer: str, row: int, col: int) -> dict[str, Any]:
        return RenderCell(
            value=designer,
            color=self.get_color("deep purple"),
            text_color=self.get_color("white"),
            col=col,
            row=row,
            bold=True,
            font_size=12,
        ).to_cell_data()

    def _build_task_cell(self, task: Any, row: int, col: int) -> dict[str, Any]:
        note = f"{task.customer}\n{task.raw_timing}"
        return RenderCell(
            value=task.name,
            note=note,
            col=col,
            row=row,
        ).to_cell_data()

    def _write_cur_time(self, cell: str = "A1") -> None:
        cur_time = pd.Timestamp.now(tz="Europe/Moscow").strftime("%H:%M %B %d")
        row, col = cell_to_indices(cell)
        self.renderer.update_cell(
            cell_data={
                "row": row + 1,
                "col": col + 1,
                "value": cur_time,
            }
        )

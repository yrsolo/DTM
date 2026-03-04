"""Calendar runtime managers extracted from core manager module."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

import pandas as pd

from core.adapters import SheetRenderAdapter
from core.render_contracts import RenderCell
from core.sheet_renderer import ServiceSheetRenderAdapter
from core.task_query_contract import query_source_tasks
from utils.func import GetColor, RGBColor, cell_to_indices, filter_stages

DEFAULT_PALETTE: dict[str, str] = {
    "white": "#FFFFFF",
    "dark_gray": "#909090",
    "med_gray": "#C0C0C0",
    "gray": "#E0E0E0",
    "light_gray": "#F0F0F0",
    "green": "#B6D7A8",
    "light_green": "#D9EAD3",
    "black": "#000000",
}


class CalendarManager:
    """Build and render designer calendar from task timing structure."""

    def __init__(
        self,
        sheet_info: Any,
        service: Any,
        repository: Any,
        renderer: SheetRenderAdapter | None = None,
        palette: Mapping[str, str] | None = None,
    ) -> None:
        self.sheet_info = sheet_info
        self.service = service
        self.calendar = None
        self.repository = repository
        self.spreadsheet_name = sheet_info.spreadsheet_name
        self.sheet_name = sheet_info.get_sheet_name("calendar")
        self.get_color = GetColor()
        self.palette = dict(DEFAULT_PALETTE)
        if palette:
            self.palette.update({str(k): str(v) for k, v in palette.items()})
        self.renderer = renderer or ServiceSheetRenderAdapter(
            service=service,
            spreadsheet_name=self.spreadsheet_name,
            sheet_name=self.sheet_name,
        )

    def create_calendar_structure(self, task_timings: dict[str, Any], answer: bool = False) -> dict[Any, Any]:
        calendar = defaultdict(lambda: defaultdict(list))
        for task in task_timings["timings"]:
            designer = task["designer"]

            for timing in task["timings"]:
                date = timing["date"]
                if answer:
                    stage = [task["name"] + " [" + s + "]" for s in timing["stage"]]
                else:
                    stage = [task["name"] + " [" + s + "]" for s in filter_stages(timing["stage"])]

                if stage:
                    stage = "\n".join(stage)
                    calendar[date][designer].append(stage)
        return calendar

    def calendar_to_dataframe(self, calendar: dict[Any, Any]) -> pd.DataFrame:
        if not calendar:
            self.calendar = pd.DataFrame()
            return self.calendar
        df = pd.DataFrame(calendar).T
        df.index.name = "Date"
        min_date = df.index.min()
        max_date = df.index.max()
        full_date_range = pd.date_range(min_date, max_date)
        df = df.reindex(full_date_range).fillna("")
        calendar = df.sort_index()
        self.calendar = calendar.reindex(sorted(calendar.columns), axis=1)
        return self.calendar

    def write_calendar_to_sheet(self, calendar: dict[Any, Any], min_date: str | None = "1W") -> None:
        df = self.calendar_to_dataframe(calendar)
        if df.empty:
            self.renderer.begin()
            if self.sheet_name:
                self.renderer.clear_cells()
            self._write_cur_time(cell="A1")
            self.renderer.execute_updates()
            return
        if min_date:
            now = pd.Timestamp.now()
            min_date = now - pd.Timedelta(min_date)
            df = df[df.index >= min_date]

        self.renderer.begin()
        if self.sheet_name:
            self.renderer.clear_cells()

        for col_num, designer in enumerate(df.columns, start=1):
            self.renderer.update_cell(
                cell_data=self._build_calendar_header_cell(col_num=col_num, designer=designer)
            )

        for row_num, (date, row) in enumerate(df.iterrows(), start=2):
            self.renderer.update_cell(cell_data=self._build_calendar_date_cell(row_num=row_num, date=date))

            now = pd.Timestamp.now().normalize()
            if date.weekday() >= 5:
                color = self.palette["light_gray"]
            else:
                color = self.palette["white"]
            if date == now:
                color = self.palette["light_green"]

            if date < now:
                text_color = self.palette["dark_gray"]
            else:
                text_color = self.palette["black"]

            for col_num, stage in enumerate(row, start=2):
                if isinstance(stage, (list, tuple)):
                    value = "\n".join(stage) if stage else ""
                elif pd.isna(stage):
                    value = ""
                else:
                    value = stage

                self.renderer.update_cell(
                    cell_data=self._build_calendar_stage_cell(
                        row_num=row_num,
                        col_num=col_num,
                        value=value,
                        color=color,
                        text_color=text_color,
                    )
                )

        self._write_cur_time(cell="A1")
        self.renderer.execute_updates()

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

    def _build_calendar_header_cell(self, col_num: int, designer: str) -> dict[str, Any]:
        return RenderCell(
            value=designer,
            color=self.get_color("deep purple"),
            text_color=self.get_color("white"),
            col=col_num + 1,
            row=1,
            bold=True,
            font_size=12,
        ).to_cell_data()

    def _build_calendar_date_cell(self, row_num: int, date: pd.Timestamp) -> dict[str, Any]:
        if date.weekday() >= 5:
            date_color = self.palette["med_gray"]
        else:
            date_color = self.palette["gray"]
        return RenderCell(
            value=date.strftime("%d.%m"),
            color=date_color,
            col=1,
            row=row_num,
        ).to_cell_data()

    def _build_calendar_stage_cell(
        self,
        row_num: int,
        col_num: int,
        value: str,
        color: Any,
        text_color: Any,
    ) -> dict[str, Any]:
        return RenderCell(
            value=value,
            color=color,
            text_color=text_color,
            col=col_num,
            row=row_num,
        ).to_cell_data()


class TaskCalendarManager:
    """Render per-task timeline calendar into dedicated sheet."""

    def __init__(
        self,
        sheet_info: Any,
        service: Any,
        repository: Any,
        renderer: SheetRenderAdapter | None = None,
        palette: Mapping[str, str] | None = None,
    ) -> None:
        self.sheet_info = sheet_info
        self.service = service
        self.calendar = None
        self.repository = repository
        self.spreadsheet_name = sheet_info.spreadsheet_name
        self.sheet_name = sheet_info.get_sheet_name("task_calendar")
        self.timeline = {}
        self.get_color = GetColor()
        self.palette = dict(DEFAULT_PALETTE)
        if palette:
            self.palette.update({str(k): str(v) for k, v in palette.items()})
        self.renderer = renderer or ServiceSheetRenderAdapter(
            service=service,
            spreadsheet_name=self.spreadsheet_name,
            sheet_name=self.sheet_name,
        )

    def get_actual_tasks(
        self,
        color_status: Sequence[str] = ("wait", "work", "pre_done"),
    ) -> dict[str, list[Any]]:
        all_tasks = self.repository.get_all_tasks()
        self.tasks = query_source_tasks(all_tasks, statuses=color_status, limit=10**9)
        self.designers = set(task.designer for task in self.tasks if task.designer)
        self.tasks_by_designer = defaultdict(list)
        for task in self.tasks:
            if task.timing:
                self.tasks_by_designer[task.designer].append(task)

        for designer, tasks in self.tasks_by_designer.items():
            self.tasks_by_designer[designer] = sorted(
                self.tasks_by_designer[designer], key=lambda x: x.min_date
            )

        return self.tasks_by_designer

    def create_timeline(
        self,
        row: int = 1,
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
        now: pd.Timestamp | None = None,
    ) -> None:
        if start is None:
            now = pd.Timestamp.now().floor("D")
            start = now - pd.Timedelta("5D")
            end = now + pd.Timedelta("30D") * 5

        self.timeline = {"now": now, "start": start, "end": end}

        day = start
        col = 2
        color = self.get_color("gray")

        while day < end:
            cell_data = self._build_timeline_cell(row=row, col=col, day=day, now=now, base_color=color)
            self.renderer.update_cell(cell_data=cell_data)
            col += 1
            day += pd.Timedelta("1D")

    def _build_timeline_cell(
        self,
        row: int,
        col: int,
        day: pd.Timestamp,
        now: pd.Timestamp,
        base_color: Any,
    ) -> dict[str, Any]:
        if day.weekday() >= 5:
            day_color = (base_color if day != now else self.get_color("green")) ** 0.25
        else:
            day_color = base_color if day != now else self.get_color("green")
        return RenderCell(
            value=day.strftime("%d.%m"),
            color=day_color,
            text_color=base_color**3,
            col=col,
            row=row,
            bold=True,
            italic=True,
            font_size=9,
        ).to_cell_data()

    def _build_task_name_cell(self, row: int, task: Any) -> dict[str, Any]:
        return RenderCell(
            value=task.name,
            note=f"Менеджер: {task.customer}\nСтатус:\n{task.status}\nТайминг:\n{task.raw_timing}",
            col=1,
            row=row,
            font_size=9,
        ).to_cell_data()

    def _build_stage_cell(
        self,
        row: int,
        col: int,
        day: pd.Timestamp,
        task: Any,
        color: Any,
        stage: str,
    ) -> dict[str, Any]:
        if day.weekday() >= 5:
            stage_color = (color if task.color_status not in ["wait"] else color.gray) ** 0.6
        else:
            stage_color = color if task.color_status not in ["wait"] else color.gray
        return RenderCell(
            value=stage[:5].upper(),
            note=f"{stage} \n{task.name}" if stage else "",
            color=stage_color,
            text_color=color**0.01,
            col=col,
            row=row,
            bold=True,
            font_size=8,
        ).to_cell_data()

    def _build_designer_cell(self, designer: str, row: int, color: Any) -> dict[str, Any]:
        return RenderCell(
            value=designer,
            color=color**1.5,
            text_color=color**0.03,
            col=1,
            row=row,
            bold=True,
            font_size=10,
        ).to_cell_data()

    def _build_timestamp_cell(self, cur_time: str) -> dict[str, Any]:
        return RenderCell(value=cur_time, col=1, row=1, bold=True).to_cell_data()

    def task_to_sheet(self, row: int, task: Any, color: Any) -> None:
        cell_data = self._build_task_name_cell(row=row, task=task)
        self.renderer.update_cell(cell_data=cell_data)

        day = max(self.timeline["start"], task.min_date)
        col = 2 + (day - self.timeline["start"]).days

        while day <= self.timeline["end"] and day <= task.max_date:
            stage = ", ".join(task.timing.get(day, [""]))
            cell_data = self._build_stage_cell(
                row=row,
                col=col,
                day=day,
                task=task,
                color=color,
                stage=stage,
            )
            self.renderer.update_cell(cell_data=cell_data)
            col += 1
            day += pd.Timedelta("1D")

    def designer_tasks_to_sheet(self, designer: str, tasks: list[Any], row: int) -> int:
        self.create_timeline(row)
        color = self.get_color()
        cell_data = self._build_designer_cell(designer=designer, row=row, color=color)
        self.renderer.update_cell(cell_data=cell_data)
        row += 1

        n = len(tasks)
        i = 0

        for task in tasks:
            e = 1 if n == 1 else 0.5 + 1.5 * (n - i) / n
            self.task_to_sheet(row, task, color**e)
            row += 1
            i += 1

        return row

    def init(self) -> None:
        self.renderer.begin()
        self.renderer.clear_cells()
        self.renderer.clear_requests()

    def write(self) -> None:
        self.renderer.execute_updates()

    def write_cur_time(self) -> None:
        cur_time = pd.Timestamp.now(tz="Europe/Moscow").strftime("%H:%M %B %d")
        cell_data = self._build_timestamp_cell(cur_time=cur_time)
        self.renderer.update_cell(cell_data=cell_data)

    def all_tasks_to_sheet(self, color_status: Sequence[str] = ("wait", "work", "pre_done")) -> None:
        self.init()
        tasks_by_designer = self.get_actual_tasks(color_status)
        row = 2
        for designer in sorted(tasks_by_designer.keys()):
            tasks = tasks_by_designer[designer]
            row = self.designer_tasks_to_sheet(designer, tasks, row)

        border_data = {
            "side": "left",
            "width": 3,
            "color": RGBColor(self.palette["green"]) ** 2,
            "worksheet_range": "G1:H50",
        }
        self.renderer.update_borders(border_data=border_data)
        self.write_cur_time()
        self.write()

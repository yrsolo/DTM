"""
Manager.py

Модуль содержит реализацию менеджера для работы с задачами и календарем.
Основные классы:
- TaskManager: Менеджер для работы с задачами.
- TaskTimingProcessor: Обработчик тайминга задач.
- CalendarManager: Менеджер для работы с календарем.

"""

from collections import defaultdict
from typing import Dict, List

import pandas as pd

from config import COLORS
from core.adapters import SheetRenderAdapter
from core.render_contracts import RenderCell
from core.repository import TimingParser
from core.sheet_renderer import ServiceSheetRenderAdapter
from utils.func import GetColor, RGBColor, cell_to_indices, filter_stages


class TaskManager:
    def __init__(self, task_repository, renderer: SheetRenderAdapter | None = None):
        self.repository = task_repository
        self.tasks = None
        self.designers = None
        self.get_color = GetColor()
        self.spreadsheet_name = self.repository.sheet_info.spreadsheet_name
        self.sheet_name = self.repository.sheet_info.get_sheet_name("designers")
        self.renderer = renderer or ServiceSheetRenderAdapter(
            service=self.repository.service,
            spreadsheet_name=self.spreadsheet_name,
            sheet_name=self.sheet_name,
        )

    def update(self):
        """Обновить данные из репозитория"""
        self.tasks = self.repository.get_all_tasks()
        self.designers = set(task.designer for task in self.tasks if task.designer)

    def task_to_table(self, color_status=("work", "pre_done")):
        """Получить задачи в виде таблицы"""
        if color_status == "all":
            color_status = ["work", "pre_done", "done"]
        elif color_status == "done":
            color_status = ["pre_done", "done"]
        elif isinstance(color_status, str):
            color_status = [color_status]

        self.update()
        tasks = [task for task in self.tasks if task.color_status in color_status]
        self.renderer.begin()
        if self.sheet_name:
            self.renderer.clear_cells()

        # Устанавливаем начальные координаты
        start_row, col = 2, 2
        row = start_row + 1

        for designer in sorted(self.designers):
            tasks_for_designer = [task for task in tasks if task.designer == designer]

            if not tasks_for_designer:
                continue

            # Добавляем имя дизайнера
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

    def _build_designer_header_cell(self, designer, row, col):
        return RenderCell(
            value=designer,
            color=self.get_color("deep purple"),
            text_color=self.get_color("white"),
            col=col,
            row=row,
            bold=True,
            font_size=12,
        ).to_cell_data()

    def _build_task_cell(self, task, row, col):
        note = f"{task.customer}\n{task.raw_timing}"
        return RenderCell(
            value=task.name,
            note=note,
            col=col,
            row=row,
        ).to_cell_data()

    def _write_cur_time(self, cell="A1"):
        cur_time = pd.Timestamp.now(tz="Europe/Moscow").strftime("%H:%M %B %d")
        row, col = cell_to_indices(cell)
        self.renderer.update_cell(
            cell_data={
                "row": row + 1,
                "col": col + 1,
                "value": cur_time,
            }
        )


def get_date_range(timings_dict: Dict[pd.Timestamp, List[str]]):
    """Возвращает минимальную и максимальную дату из словаря тайминга"""
    min_date = min(timings_dict.keys())
    max_date = max(timings_dict.keys())
    return min_date, max_date


class TaskTimingProcessor:
    """Класс для обработки тайминга задач"""

    def create_task_timing_structure(self, tasks):
        """
        Создает структуру тайминга для задачи
        """
        global_min_date = pd.Timestamp.max
        global_max_date = pd.Timestamp.min

        task_structure = []
        parser = TimingParser()
        for task in tasks:
            timings_dict = parser.parse(task.raw_timing)
            if not timings_dict:
                continue
            min_date, max_date = get_date_range(timings_dict)
            global_min_date = min(global_min_date, min_date)
            global_max_date = max(global_max_date, max_date)
            timings_list = [{"date": date, "stage": stage} for date, stage in timings_dict.items()]
            task_structure.append(
                {
                    "id": task.id,
                    "name": task.name,
                    "designer": task.designer,
                    "customer": task.customer,
                    "status": task.status,
                    "color_status": task.color_status,
                    "timings": timings_list,
                    "min_date": min_date,
                    "max_date": max_date,
                }
            )
        return {"timings": task_structure, "min_date": global_min_date, "max_date": global_max_date}


class CalendarManager:
    def __init__(
        self,
        sheet_info,
        service,
        repository,
        renderer: SheetRenderAdapter | None = None,
    ):
        self.sheet_info = sheet_info
        self.service = service
        self.calendar = None
        self.repository = repository
        self.spreadsheet_name = sheet_info.spreadsheet_name
        self.sheet_name = sheet_info.get_sheet_name("calendar")
        self.get_color = GetColor()
        self.renderer = renderer or ServiceSheetRenderAdapter(
            service=service,
            spreadsheet_name=self.spreadsheet_name,
            sheet_name=self.sheet_name,
        )

    def create_calendar_structure(self, task_timings, answer=False):
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

    def calendar_to_dataframe(self, calendar):
        df = pd.DataFrame(calendar).T
        df.index.name = "Date"
        min_date = df.index.min()
        max_date = df.index.max()
        full_date_range = pd.date_range(min_date, max_date)
        df = df.reindex(full_date_range).fillna("")
        calendar = df.sort_index()
        self.calendar = calendar.reindex(sorted(calendar.columns), axis=1)
        return self.calendar

    def write_calendar_to_sheet(self, calendar, min_date="1W"):
        df = self.calendar_to_dataframe(calendar)
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
                color = COLORS["light_gray"]
            else:
                color = COLORS["white"]
            if date == now:
                color = COLORS["light_green"]

            if date < now:
                text_color = COLORS["dark_gray"]
            else:
                text_color = COLORS["black"]

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

    def _write_cur_time(self, cell="A1"):
        cur_time = pd.Timestamp.now(tz="Europe/Moscow").strftime("%H:%M %B %d")
        row, col = cell_to_indices(cell)
        self.renderer.update_cell(
            cell_data={
                "row": row + 1,
                "col": col + 1,
                "value": cur_time,
            }
        )

    def _build_calendar_header_cell(self, col_num, designer):
        return RenderCell(
            value=designer,
            color=self.get_color("deep purple"),
            text_color=self.get_color("white"),
            col=col_num + 1,
            row=1,
            bold=True,
            font_size=12,
        ).to_cell_data()

    def _build_calendar_date_cell(self, row_num, date):
        if date.weekday() >= 5:
            date_color = COLORS["med_gray"]
        else:
            date_color = COLORS["gray"]
        return RenderCell(
            value=date.strftime("%d.%m"),
            color=date_color,
            col=1,
            row=row_num,
        ).to_cell_data()

    def _build_calendar_stage_cell(self, row_num, col_num, value, color, text_color):
        return RenderCell(
            value=value,
            color=color,
            text_color=text_color,
            col=col_num,
            row=row_num,
        ).to_cell_data()


class TaskCalendarManager:
    def __init__(
        self,
        sheet_info,
        service,
        repository,
        renderer: SheetRenderAdapter | None = None,
    ):
        self.sheet_info = sheet_info
        self.service = service
        self.calendar = None
        self.repository = repository
        self.spreadsheet_name = sheet_info.spreadsheet_name
        self.sheet_name = sheet_info.get_sheet_name("task_calendar")
        self.timeline = {}
        self.get_color = GetColor()
        self.renderer = renderer or ServiceSheetRenderAdapter(
            service=service,
            spreadsheet_name=self.spreadsheet_name,
            sheet_name=self.sheet_name,
        )

    def get_actual_tasks(self, color_status=("wait", "work", "pre_done")):
        self.tasks = self.repository.get_task_by_color_status(color_status)
        self.designers = set(task.designer for task in self.tasks if task.designer)
        self.tasks_by_designer = defaultdict(list)
        for task in self.tasks:
            if task.timing:
                self.tasks_by_designer[task.designer].append(task)

        # Сортируем задачи по дате
        for designer, tasks in self.tasks_by_designer.items():
            self.tasks_by_designer[designer] = sorted(
                self.tasks_by_designer[designer], key=lambda x: x.min_date
            )

        return self.tasks_by_designer

    def create_timeline(
        self,
        row: int = 1,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
        now: pd.Timestamp = None,
    ):

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

        # self.service.execute_updates()

    def _build_timeline_cell(self, row, col, day, now, base_color):
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

    def _build_task_name_cell(self, row, task):
        return RenderCell(
            value=task.name,
            note=f"Менеджер: {task.customer}\nСтатус:\n{task.status}\nТайминг:\n{task.raw_timing}",
            col=1,
            row=row,
            font_size=9,
        ).to_cell_data()

    def _build_stage_cell(self, row, col, day, task, color, stage):
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

    def _build_designer_cell(self, designer, row, color):
        return RenderCell(
            value=designer,
            color=color**1.5,
            text_color=color**0.03,
            col=1,
            row=row,
            bold=True,
            font_size=10,
        ).to_cell_data()

    def _build_timestamp_cell(self, cur_time):
        return RenderCell(value=cur_time, col=1, row=1, bold=True).to_cell_data()

    def task_to_sheet(self, row, task, color):
        # task name
        cell_data = self._build_task_name_cell(row=row, task=task)
        self.renderer.update_cell(cell_data=cell_data)

        day = max(self.timeline["start"], task.min_date)
        col = 2 + (day - self.timeline["start"]).days
        # task.timings

        while day <= self.timeline["end"] and day <= task.max_date:
            stage = ", ".join(task.timing.get(day, [""]))
            # print(day,col, stage)
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

    def designer_tasks_to_sheet(self, designer, tasks, row):
        # timelint
        self.create_timeline(row)
        # task name
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

    def init(self):
        self.renderer.begin()
        self.renderer.clear_cells()
        self.renderer.clear_requests()

    def write(self):
        self.renderer.execute_updates()

    def write_cur_time(self):
        cur_time = pd.Timestamp.now(tz="Europe/Moscow").strftime("%H:%M %B %d")
        cell_data = self._build_timestamp_cell(cur_time=cur_time)
        self.renderer.update_cell(cell_data=cell_data)

    def all_tasks_to_sheet(self, color_status=("wait", "work", "pre_done")):
        """main"""
        self.init()

        tasks_by_designer = self.get_actual_tasks(color_status)
        row = 2
        for designer in sorted(tasks_by_designer.keys()):
            tasks = tasks_by_designer[designer]
            row = self.designer_tasks_to_sheet(designer, tasks, row)

        # border at currant day
        border_data = {
            "side": "left",
            "width": 3,
            "color": RGBColor(COLORS["green"]) ** 2,
            "worksheet_range": "G1:H50",
        }
        self.renderer.update_borders(border_data=border_data)
        self.write_cur_time()
        self.write()



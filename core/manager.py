"""
Manager.py

Модуль содержит реализацию менеджера для работы с задачами и календарем.
Основные классы:
- TaskManager: Менеджер для работы с задачами.
- TaskTimingProcessor: Обработчик тайминга задач.
- CalendarManager: Менеджер для работы с календарем.

"""

import datetime
from collections import defaultdict
from typing import Dict, List

import pandas as pd

from config import COLORS
from core.render_contracts import RenderCell
from core.repository import TimingParser
from utils.func import GetColor, RGBColor, cell_to_indices, filter_stages


class TaskManager:
    def __init__(self, task_repository):
        self.repository = task_repository
        self.tasks = None
        self.designers = None
        self.get_color = GetColor()

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
        # Получаем ID дизайнерского листа
        spreadsheet_name = self.repository.sheet_info.spreadsheet_name
        sheet_name = self.repository.sheet_info.get_sheet_name("designers")
        # Очищаем лист
        self.repository.service.clear_cells(spreadsheet_name, sheet_name)

        # Устанавливаем начальные координаты
        start_row, col = 2, 2
        row = start_row + 1

        for designer in sorted(self.designers):
            tasks_for_designer = [task for task in tasks if task.designer == designer]

            if not tasks_for_designer:
                continue

            # Добавляем имя дизайнера
            cell_data = {
                "value": designer,
                "color": self.get_color("deep purple"),
                "text_color": self.get_color("white"),
                "col": col,
                "row": start_row,
                "bold": True,
                # 'italic': True,
                "font_size": 12,
            }
            self.repository.service.update_cell(spreadsheet_name, sheet_name, cell_data=cell_data)

            for task in tasks_for_designer:
                note = str(task.customer) + "\n" + str(task.raw_timing)
                self.repository.service.update_cell(
                    spreadsheet_name, sheet_name, row, col, value=task.name, note=note
                )
                row += 1

            col += 1
            row = start_row + 1

        write_cur_time(self.repository.service, spreadsheet_name, sheet_name, cell="A1")
        self.repository.service.execute_updates(spreadsheet_name)


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
    def __init__(self, sheet_info, service, repository):
        self.sheet_info = sheet_info
        self.service = service
        self.calendar = None
        self.repository = repository
        self.get_color = GetColor()

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
                    # calendar[date] = task['id']
        return calendar

    def calendar_to_dataframe(self, calendar):
        # Преобразуем словарь в DataFrame
        df = pd.DataFrame(calendar).T
        df.index.name = "Date"
        # Добавляем пропущенные даты
        min_date = df.index.min()
        max_date = df.index.max()
        full_date_range = pd.date_range(min_date, max_date)
        df = df.reindex(full_date_range).fillna("")
        # Преобразуем списки этапов в строки
        calendar = df.sort_index()
        self.calendar = calendar.reindex(sorted(calendar.columns), axis=1)
        return self.calendar

    def write_calendar_to_sheet(self, calendar, min_date="1W"):
        df = self.calendar_to_dataframe(calendar)
        if min_date:
            now = pd.Timestamp.now()
            min_date = now - pd.Timedelta(min_date)
            df = df[df.index >= min_date]
        spreadsheet_name = self.sheet_info.spreadsheet_name
        sheet_name = self.sheet_info.get_sheet_name("calendar")

        # Очищаем лист
        if sheet_name:
            self.service.clear_cells(spreadsheet_name, sheet_name)

        # Записываем имена дизайнеров (заголовок таблицы)
        for col_num, designer in enumerate(df.columns, start=1):
            cell_data = {
                "value": designer,
                "color": self.get_color("deep purple"),
                "text_color": self.get_color("white"),
                "col": col_num + 1,
                "row": 1,
                "bold": True,
                # 'italic': True,
                "font_size": 12,
            }
            self.service.update_cell(spreadsheet_name, sheet_name, cell_data=cell_data)

        # Записываем данные в Google Таблицу
        for row_num, (date, row) in enumerate(df.iterrows(), start=2):
            # Записываем дату слева от этапов
            if date.weekday() >= 5:  # проверяем на выходные дни
                color = COLORS["med_gray"]
            else:
                color = COLORS["gray"]

            self.service.update_cell(
                spreadsheet_name,
                sheet_name,
                row_num,
                1,
                value=date.strftime("%d.%m"),
                color=color,
            )
            now = pd.Timestamp.now().normalize()
            if date.weekday() >= 5:  # проверяем на выходные дни
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

                self.service.update_cell(
                    spreadsheet_name,
                    sheet_name,
                    row_num,
                    col_num,
                    value=value,
                    color=color,
                    text_color=text_color,
                )

        write_cur_time(self.service, spreadsheet_name, sheet_name, cell="A1")
        self.service.execute_updates(spreadsheet_name)

def write_cur_time(service, spreadsheet_name, sheet_name, cell="A1"):
    cur_time = pd.Timestamp.now(tz="Europe/Moscow").strftime("%H:%M %B %d")
    row, col = cell_to_indices(cell)
    service.update_cell(spreadsheet_name, sheet_name, row + 1, col + 1, value=cur_time)


class TaskCalendarManager:
    def __init__(self, sheet_info, service, repository):
        self.sheet_info = sheet_info
        self.service = service
        self.calendar = None
        self.repository = repository
        self.spreadsheet_name = sheet_info.spreadsheet_name
        self.sheet_name = sheet_info.get_sheet_name("task_calendar")
        self.timeline = {}
        self.get_color = GetColor()

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
            if day.weekday() >= 5:
                day_color = (color if day != now else self.get_color("green")) ** 0.25
            else:
                day_color = color if day != now else self.get_color("green")

            cell_data = RenderCell(
                value=day.strftime("%d.%m"),
                color=day_color,
                text_color=color**3,
                col=col,
                row=row,
                bold=True,
                italic=True,
                font_size=9,
            ).to_cell_data()

            self.service.update_cell(cell_data=cell_data)
            col += 1
            day += pd.Timedelta("1D")

        # self.service.execute_updates()

    def task_to_sheet(self, row, task, color):
        # task name
        cell_data = RenderCell(
            value=task.name,
            note=f"Менеджер: {task.customer}\nСтатус:\n{task.status}\nТайминг:\n{task.raw_timing}",
            col=1,
            row=row,
            font_size=9,
        ).to_cell_data()
        self.service.update_cell(cell_data=cell_data)

        day = max(self.timeline["start"], task.min_date)
        col = 2 + (day - self.timeline["start"]).days
        # task.timings

        while day <= self.timeline["end"] and day <= task.max_date:
            stage = ", ".join(task.timing.get(day, [""]))
            # print(day,col, stage)
            if day.weekday() >= 5:
                stage_color = (
                    color if task.color_status not in ["wait"] else color.gray
                ) ** 0.6
            else:
                stage_color = color if task.color_status not in ["wait"] else color.gray

            cell_data = RenderCell(
                value=stage[:5].upper(),
                note=f"{stage} \n{task.name}" if stage else "",
                color=stage_color,
                text_color=color**0.01,
                col=col,
                row=row,
                bold=True,
                font_size=8,
            ).to_cell_data()

            self.service.update_cell(cell_data=cell_data)

            col += 1
            day += pd.Timedelta("1D")

    def designer_tasks_to_sheet(self, designer, tasks, row):
        # timelint
        self.create_timeline(row)
        # task name
        color = self.get_color()
        cell_data = RenderCell(
            value=designer,
            color=color**1.5,
            text_color=color**0.03,
            col=1,
            row=row,
            bold=True,
            font_size=10,
        ).to_cell_data()
        self.service.update_cell(cell_data=cell_data)
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
        self.service.set_spreadsheet_and_worksheet(self.spreadsheet_name, self.sheet_name)
        self.service.clear_cells()
        self.service.clear_requests()

    def write(self):
        self.service.execute_updates()

    def write_cur_time(self):
        cur_time = pd.Timestamp.now(tz="Europe/Moscow").strftime("%H:%M %B %d")
        cell_data = RenderCell(value=cur_time, col=1, row=1, bold=True).to_cell_data()
        self.service.update_cell(cell_data=cell_data)

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
        self.service.update_borders(border_data=border_data)
        self.write_cur_time()
        self.write()


class TaskCalendarManagerOld(CalendarManager):
    def create_task_calendar_structure(self, task_timings):
        calendar = defaultdict(lambda: defaultdict(list))
        for task in task_timings["timings"]:
            task_id = task["id"]
            for timing in task["timings"]:
                date = timing["date"]
                stage = timing["stage"]
                calendar[date][task_id].append(stage)
        return calendar

    def task_calendar_to_dataframe(self, calendar):
        # Преобразуем словарь в DataFrame
        calendar = pd.DataFrame(calendar).T

        calendar.index.name = "Date"
        date_range = [dict(), dict()]

        notes = defaultdict(lambda: defaultdict(str))
        calendar = calendar.sort_index()
        for task_id, col in calendar.items():
            date_range[0][task_id] = col.dropna().index.min()
            date_range[1][task_id] = col.dropna().index.max()
            for date, stages in col.items():
                if isinstance(stages, (list, tuple)):
                    pass
                elif pd.isna(stages):
                    continue
                main_stage = stages[0][0][0:3]
                s = ["\n".join(s) for s in stages]
                notes[pd.to_datetime(date)][task_id] = "\n".join(s)
                calendar.loc[date, task_id] = main_stage.upper() if main_stage != "отв" else "ответ"

        # Добавляем пропущенные даты
        min_date = calendar.index.min()
        max_date = calendar.index.max()
        full_date_range = pd.date_range(min_date, max_date)
        calendar = calendar.reindex(full_date_range).fillna("")

        sort_tasks = sorted(
            calendar.columns,
            key=lambda x: date_range[1][x] if date_range[1][x] else datetime.date.max,
            reverse=True,
        )
        self.calendar = calendar.reindex(sort_tasks, axis=1).T
        return self.calendar, notes, date_range

    def write_task_calendar_to_sheet(self, calendar, min_date="1W"):
        spreadsheet_name = self.sheet_info.spreadsheet_name
        sheet_name = self.sheet_info.get_sheet_name("task_calendar")

        calendar, notes, date_range = self.task_calendar_to_dataframe(calendar)
        if min_date:
            now = pd.Timestamp.now()
            min_date = now - pd.Timedelta(min_date)
            calendar = calendar.T[calendar.T.index >= min_date].T

        # Очищаем лист
        if sheet_name:
            self.service.clear_cells(spreadsheet_name, sheet_name)

        # Записываем имена проектов (заголовок таблицы)
        for row_num, (task_id, _) in enumerate(calendar.iterrows(), start=2):
            task = self.repository.tasks[task_id]
            task_note = "Designer: {}\nCustomer: {}\nStatus: {}".format(
                task.designer, task.customer, task.status
            )
            if task.color_status == "wait":
                color = COLORS["gray"]
            else:
                color = COLORS["white"]

            self.service.update_cell(
                spreadsheet_name,
                sheet_name,
                row_num,
                1,
                value=task.name,
                note=task_note,
                color=color,
            )

        # Записываем данные в Google Таблицу
        for col_num, (date, col) in enumerate(calendar.items(), start=2):
            # Записываем дату слева от этапов
            if date.weekday() >= 5:  # проверяем на выходные дни
                color = COLORS["med_gray"]
            else:
                color = COLORS["gray"]

            self.service.update_cell(
                spreadsheet_name,
                sheet_name,
                1,
                col_num,
                value=date.strftime("%d.%m"),
                color=color,
            )
            now = pd.Timestamp.now().normalize()

            for row_num, (task_id, stage) in enumerate(col.items(), start=2):
                task = self.repository.tasks[task_id]

                if date <= date_range[1][task_id]:
                    if task.color_status == "wait":
                        if date.weekday() >= 5:
                            color = COLORS["med_gray"]
                        else:
                            color = COLORS["gray"]
                    else:
                        color = COLORS["light_green"]
                    pass
                else:
                    if date.weekday() >= 5:  # проверяем на выходные дни
                        color = COLORS["gray"]
                    else:
                        color = COLORS["white"]

                text_color = None

                if date == now:
                    color = COLORS["green"]

                if pd.isna(stage):
                    value = ""
                    note = ""
                else:
                    value = stage
                    note = notes[date][task_id]
                self.service.update_cell(
                    spreadsheet_name,
                    sheet_name,
                    row_num,
                    col_num,
                    value=value,
                    color=color,
                    text_color=text_color,
                    note=note,
                )

        write_cur_time(self.service, spreadsheet_name, sheet_name, cell="A1")
        self.service.execute_updates(spreadsheet_name)


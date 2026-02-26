"""
Manager.py

Модуль содержит реализацию менеджера для работы с задачами и календарем.
Основные классы:
- TaskManager: Менеджер для работы с задачами.
- TaskTimingProcessor: Обработчик тайминга задач.
- CalendarManager: Менеджер для работы с календарем.

"""

from typing import List, Dict
import datetime
import pandas as pd
from collections import defaultdict
from core.repository import TimingParser
from utils.func import filter_stages, cell_to_indices
from config import COLORS


class TaskManager:
    def __init__(self, task_repository):
        self.repository = task_repository
        self.tasks = None
        self.designers = None

    def update(self):
        """ Обновить данные из репозитория"""
        self.tasks = self.repository.get_all_tasks()
        self.designers = set(task.designer for task in self.tasks if task.designer)

    def task_to_table(self, color_status=('work', 'pre_done')):
        """ Получить задачи в виде таблицы"""
        if color_status == 'all':
            color_status = ['work', 'pre_done', 'done']
        elif color_status == 'done':
            color_status = ['pre_done', 'done']
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
            self.repository.service.update_cell(
                spreadsheet_name, sheet_name, start_row, col, value=designer, text_color=COLORS['white']
            )

            for task in tasks_for_designer:
                note = str(task.customer) + '\n' + str(task.raw_timing)
                self.repository.service.update_cell(
                    spreadsheet_name, sheet_name, row, col,
                    value=task.name, note=note
                )
                row += 1

            col += 1
            row = start_row + 1

        write_cur_time(self.repository.service, spreadsheet_name, sheet_name, cell='A1')
        self.repository.service.execute_updates(spreadsheet_name)


def get_date_range(timings_dict: Dict[pd.Timestamp, List[str]]):
    """ Возвращает минимальную и максимальную дату из словаря тайминга """
    min_date = min(timings_dict.keys())
    max_date = max(timings_dict.keys())
    return min_date, max_date


class TaskTimingProcessor:
    """ Класс для обработки тайминга задач """

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
            task_structure.append({
                "id": task.id,
                "name": task.name,
                "designer": task.designer,
                "customer": task.customer,
                "status": task.status,
                "color_status": task.color_status,
                "timings": timings_list,
                "min_date": min_date,
                "max_date": max_date
            })
        return {
            'timings': task_structure,
            'min_date': global_min_date,
            'max_date': global_max_date
        }


class CalendarManager:
    def __init__(self, sheet_info, service, repository):
        self.sheet_info = sheet_info
        self.service = service
        self.calendar = None
        self.repository = repository

    def create_calendar_structure(self, task_timings, answer=False):
        calendar = defaultdict(lambda: defaultdict(list))
        for task in task_timings['timings']:
            designer = task['designer']

            for timing in task['timings']:
                date = timing['date']
                if answer:
                    stage = [task['name'] + ' [' + s + ']' for s in timing['stage']]
                else:
                    stage = [task['name'] + ' [' + s + ']' for s in filter_stages(timing['stage'])]

                if stage:
                    stage = '\n'.join(stage)
                    calendar[date][designer].append(stage)
                    # calendar[date] = task['id']
        return calendar

    def calendar_to_dataframe(self, calendar):
        # Преобразуем словарь в DataFrame
        df = pd.DataFrame(calendar).T
        df.index.name = 'Date'
        # Добавляем пропущенные даты
        min_date = df.index.min()
        max_date = df.index.max()
        full_date_range = pd.date_range(min_date, max_date)
        df = df.reindex(full_date_range).fillna("")
        # Преобразуем списки этапов в строки
        calendar = df.sort_index()
        self.calendar = calendar.reindex(sorted(calendar.columns), axis=1)
        return self.calendar

    def write_calendar_to_sheet(self, calendar, min_date='1W'):
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
            self.service.update_cell(spreadsheet_name, sheet_name, 1, col_num + 1, value=designer,
                                     text_color=COLORS['white'])

        # Записываем данные в Google Таблицу
        for row_num, (date, row) in enumerate(df.iterrows(), start=2):
            # Записываем дату слева от этапов
            if date.weekday() >= 5:  # проверяем на выходные дни
                color = COLORS['med_gray']
            else:
                color = COLORS['gray']

            self.service.update_cell(spreadsheet_name, sheet_name, row_num, 1, value=date.strftime('%d.%m'),
                                     color=color, )
            now = pd.Timestamp.now().normalize()
            if date.weekday() >= 5:  # проверяем на выходные дни
                color = COLORS['light_gray']
            else:
                color = COLORS['white']
            if date == now:
                color = COLORS['light_green']

            if date < now:
                text_color = COLORS['dark_gray']
            else:
                text_color = None

            for col_num, stage in enumerate(row, start=2):
                if isinstance(stage, (list, tuple)):
                    value = "\n".join(stage) if stage else ""
                elif pd.isna(stage):
                    value = ""
                else:
                    value = stage

                self.service.update_cell(spreadsheet_name, sheet_name, row_num, col_num, value=value, color=color,
                                         text_color=text_color)

        write_cur_time(self.service, spreadsheet_name, sheet_name, cell='A1')
        self.service.execute_updates(spreadsheet_name)


def write_cur_time(service, spreadsheet_name, sheet_name, cell='A1'):
    cur_time = pd.Timestamp.now(tz='Europe/Moscow').strftime('%H:%M')
    row, col = cell_to_indices(cell)
    service.update_cell(spreadsheet_name, sheet_name, row+1, col+1, value=cur_time)


class TaskCalendarManager(CalendarManager):

    def create_task_calendar_structure(self, task_timings):
        calendar = defaultdict(lambda: defaultdict(list))
        for task in task_timings['timings']:
            task_id = task['id']
            for timing in task['timings']:
                date = timing['date']
                stage = timing['stage']
                calendar[date][task_id].append(stage)
        return calendar

    def task_calendar_to_dataframe(self, calendar):
        # Преобразуем словарь в DataFrame
        calendar = pd.DataFrame(calendar).T

        calendar.index.name = 'Date'
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
                s = ['\n'.join(s) for s in stages]
                notes[pd.to_datetime(date)][task_id] = '\n'.join(s)
                calendar.loc[date, task_id] = main_stage.upper() if main_stage != 'отв' else 'ответ'

        # Добавляем пропущенные даты
        min_date = calendar.index.min()
        max_date = calendar.index.max()
        full_date_range = pd.date_range(min_date, max_date)
        calendar = calendar.reindex(full_date_range).fillna("")

        sort_tasks = sorted(calendar.columns, key=lambda x: date_range[1][x] if date_range[1][x] else datetime.date.max,
                            reverse=True)
        self.calendar = calendar.reindex(sort_tasks, axis=1).T
        return self.calendar, notes, date_range

    def write_task_calendar_to_sheet(self, calendar, min_date='1W'):
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
            if task.color_status == 'wait':
                color = COLORS['gray']
            else:
                color = COLORS['white']

            self.service.update_cell(spreadsheet_name, sheet_name, row_num, 1, value=task.name, note=task_note,
                                     color=color)

        # Записываем данные в Google Таблицу
        for col_num, (date, col) in enumerate(calendar.items(), start=2):
            # Записываем дату слева от этапов
            if date.weekday() >= 5:  # проверяем на выходные дни
                color = COLORS['med_gray']
            else:
                color = COLORS['gray']

            self.service.update_cell(spreadsheet_name, sheet_name, 1, col_num, value=date.strftime('%d.%m'),
                                     color=color, )
            now = pd.Timestamp.now().normalize()

            for row_num, (task_id, stage) in enumerate(col.items(), start=2):
                task = self.repository.tasks[task_id]

                if date <= date_range[1][task_id]:
                    if task.color_status == 'wait':
                        if date.weekday() >= 5:
                            color = COLORS['med_gray']
                        else:
                            color = COLORS['gray']
                    else:
                        color = COLORS['light_green']
                    pass
                else:
                    if date.weekday() >= 5:  # проверяем на выходные дни
                        color = COLORS['gray']
                    else:
                        color = COLORS['white']

                text_color = None

                if date == now:
                    color = COLORS['green']

                if pd.isna(stage):
                    value = ""
                    note = ""
                else:
                    value = stage
                    note = notes[date][task_id]
                self.service.update_cell(spreadsheet_name, sheet_name, row_num, col_num, value=value, color=color,
                                         text_color=text_color, note=note)

        write_cur_time(self.service, spreadsheet_name, sheet_name, cell='A1')
        self.service.execute_updates(spreadsheet_name)

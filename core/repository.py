"""
Модуль содержит реализацию репозиториев для работы с задачами, включая получение, обработку и фильтрацию данных.

Основные классы:
- Task: представление задачи в системе.
- TaskRepository: базовый интерфейс репозитория для работы с задачами.
- GoogleSheetsTaskRepository: реализация репозитория для работы с Google Таблицами.
"""

import datetime
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from typing import List, Dict

import pandas as pd

from config import TASK_FIELD_MAP, REPLACE_NAMES, COLOR_STATUS
from core.reminder import TelegramNotifier
from utils.service import GoogleSheetInfo, GoogleSheetsService


class TimingParser:
    """Парсер тайминга задач."""

    def __init__(self):
        """Инициализация парсера тайминга."""
        self.date_pattern = re.compile(r"(\d{2}\.\d{2})")
        self.logger = TelegramNotifier()

    def parse(self, timing_str: str) -> Dict[pd.Timestamp, List[str]]:
        """Преобразует строку тайминга в словарь, где ключи - даты, значения - списки этапов задач.

        Args:
            timing_str: Строка тайминга.

        Returns:
            dict: Словарь с датами и этапами задач.

        """
        timings = defaultdict(list)

        # Разбиваем строку на отдельные строки по переносам
        if timing_str is None:
            return timings
        lines = timing_str.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Ищем дату в начале строки
            match = self.date_pattern.match(line)
            if not match:
                continue

            date_str = match.group(1)
            stage = line[len(date_str):].strip().strip('-').strip()
            if not pd.isna(stage):
                # Преобразуем строку даты в объект pandas.Timestamp
                year = datetime.datetime.now().year
                month = date_str[3:]
                day = date_str[:2]
                formatted_date_str = f'{year}-{month}-{day}'
                try:
                    # Попытка преобразования даты
                    date = pd.Timestamp(formatted_date_str)
                except ValueError as e:
                    # Обработка ошибки и вывод строки, которую не удалось преобразовать
                    err_text = f"""Ошибка преобразования даты: {formatted_date_str}
Строка тайминга: {line}
Подробности ошибки: {e}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
                    print(err_text)
                    self.logger.log(err_text)
                    date = pd.Timestamp.now()

                if date < (pd.Timestamp.now() - pd.DateOffset(months=5)):
                    date = date + pd.DateOffset(years=1)
                elif date > (pd.Timestamp.now() + pd.DateOffset(months=6)):
                    date = date - pd.DateOffset(years=1)
                timings[date].append(stage)

        return dict(timings)


class Task:
    def __init__(self, brand, format_, project_name, customer, designer, raw_timing, status, color, color_status, name,
                 task_id, parser=None):
        self.brand = brand
        self.format_ = format_
        self.project_name = project_name
        self.customer = customer
        self.designer = designer
        self.raw_timing = raw_timing
        self.timing_cache = None
        self.status = status
        self.color = color
        self.color_status = color_status
        self.name = name
        self.id = task_id
        self.parser = parser or TimingParser()

    def __repr__(self):
        return f'{self.id} {self.name}'

    @property
    def timing(self):
        if self.timing_cache:
            return self.timing_cache
        else:
            self.timing_cache = self.parser.parse(self.raw_timing)
            return self.timing_cache

    @property
    def max_date(self):
        return max(self.timing.keys()) if self.timing else None

    @property
    def min_date(self):
        return min(self.timing.keys()) if self.timing else None


# 2. Репозитории
# Определим интерфейсы и базовую реализацию:

class TaskRepository(ABC):
    """ Репозиторий для работы с задачами"""

    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        pass


def _determine_status_from_color(color):
    """ Определить статус по цвету"""
    cs = COLOR_STATUS
    return cs.get(color, "unknown")


class GoogleSheetsTaskRepository(TaskRepository):
    """ Репозиторий для работы с задачами в Google Таблицах"""

    def __init__(self, sheet_info: GoogleSheetInfo, service: GoogleSheetsService):
        self.sheet_info = sheet_info
        self.service = service
        self.df = None
        self.replace_names = REPLACE_NAMES
        self.tasks = dict()
        self.timing_parser = TimingParser()

    def get_all_tasks(self) -> List[Task]:
        """ Получить все задачи"""
        self._load()
        return [task for task in self.tasks.values()]

    def get_tasks_by_date(self, date):
        """ Получить задачи по дате"""
        self._load()
        tasks = self.get_task_by_color_status(['work'])
        return [task for task in tasks if date in task.timing.keys()]

    def get_task_by(self, column_name, value):
        """ Получить задачи по значению в колонке"""
        ids = self._filter(column_name, value)['id']
        return self.get_task_by_id(ids)

    def get_task_by_id(self, task_ids):
        self._load()
        if isinstance(task_ids, Iterable):
            return [self.tasks[task_id] for task_id in task_ids]
        else:
            return self.tasks[task_ids]

    def get_task_by_color_status(self, color_status):
        """ Получить задачи по цветовому статусу"""
        return self.get_task_by('color_status', color_status)

    def _load_and_process_data(self):
        """ Загрузить и обработать данные из Google Таблицы"""
        spreadsheet_name = self.sheet_info.spreadsheet_name
        sheet_name = self.sheet_info.get_sheet_name("tasks")
        df = self.service.get_dataframe(spreadsheet_name, sheet_name)
        color_range = f'A2:A{len(df) + 1}'
        colors = self.service.get_cell_colors(spreadsheet_name, sheet_name, color_range)
        # в ячейке ДИЗАЙНЕР может быть несколько человек, там str в котором на каждой строчке один человек
        # надо эти строчки отсортировать по алфавиту удалив лишние пробелы в начале и конце каждоый строки
        df['ДИЗАЙНЕР'] = df['ДИЗАЙНЕР'].fillna('')
        df['ДИЗАЙНЕР'] = df['ДИЗАЙНЕР'].apply(
            lambda x: '\n'.join(sorted([i.strip() for i in x.split('\n') if i.strip()])))
        df['ДИЗАЙНЕР'] = df['ДИЗАЙНЕР'].apply(lambda x: '[Не назначен]' if x == '' else x)
        df['color'] = colors
        df['color_status'] = df['color'].apply(_determine_status_from_color)
        df['id'] = df.index + 2
        df['name'] = df.apply(self._generate_task_name, axis=1)
        self.df = df
        self._df_to_task(df)

    def _generate_task_name(self, row):
        """ Сгенерировать название задачи"""
        format_ = row['ФОРМАТ'].split('\n')[0] if row['ФОРМАТ'] else ''
        name = str(row['БРЕНД']) + " [" + str(row['ПРОЕКТ']) + "] " + str(format_)
        for key, value in self.replace_names.items():
            name = name.replace(key, value)
        return name

    def _load(self):
        """ Проверить наличие данных"""
        if self.df is None:
            self._load_and_process_data()

    def _df_to_task(self, df):
        """ Преобразовать DataFrame в список задач"""
        tasks_list = []
        for idx, row in df.iterrows():
            task = {key: row[value] for key, value in TASK_FIELD_MAP.items()}
            task = Task(**task, parser=self.timing_parser)
            tasks_list.append(task)
            self.tasks[task.id] = task
        return tasks_list

    def _filter(self, column_name, value):
        """ Отфильтровать DataFrame по значению в колонке"""
        self._load()
        # если не кортеж или список, то преобразуем в список
        if not isinstance(value, Iterable):
            value = [value]
        return self.df[self.df[column_name].isin(value)]

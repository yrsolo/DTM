"""
Модуль содержит реализацию репозиториев для работы с задачами, включая получение, обработку и фильтрацию данных.

Основные классы:
- Task: представление задачи в системе.
- TaskRepository: базовый интерфейс репозитория для работы с задачами.
- GoogleSheetsTaskRepository: реализация репозитория для работы с Google Таблицами.
"""

import re
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from typing import Dict, List

import pandas as pd

from config import COLOR_STATUS, REPLACE_NAMES, TASK_FIELD_MAP
from core.contracts import TaskRowContract, is_nullish, normalize_text
from core.errors import MissingRequiredColumnsError, RowValidationIssue
from core.reminder import TelegramNotifier
from utils.service import GoogleSheetInfo, GoogleSheetsService


def _is_nullish(value) -> bool:
    """Compatibility wrapper for local module usage."""
    return is_nullish(value)


def _normalize_text(value, strip: bool = True) -> str:
    """Compatibility wrapper for local module usage."""
    return normalize_text(value, strip=strip)


class TimingParser:
    """Парсер тайминга задач."""

    def __init__(self):
        """Инициализация парсера тайминга."""
        self.date_pattern = re.compile(r"(\d{2}\.\d{2})")
        self.logger = TelegramNotifier()

    def parse(
        self, timing_str: str, next_task_date: pd.Timestamp = None
    ) -> Dict[pd.Timestamp, List[str]]:
        """Преобразует строку тайминга в словарь, где ключи - даты, значения - списки этапов задач.

        Args:
            timing_str: Строка тайминга.
            next_task_date: дата соседней задачи (для определения года)

        Returns:
            dict: Словарь с датами и этапами задач.

        """
        if next_task_date is None:
            next_task_date = pd.Timestamp.now()
        timings = defaultdict(list)

        # Разбиваем строку на отдельные строки по переносам.
        if _is_nullish(timing_str):
            return timings
        timing_str = str(timing_str)
        if not timing_str.strip():
            return timings
        lines = timing_str.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Ищем дату в начале строки
            match = self.date_pattern.match(line)
            if not match:
                continue

            date_str = match.group(1)
            stage = line[len(date_str) :].strip().strip("-").strip()
            if stage:
                # Преобразуем строку даты в объект pandas.Timestamp
                # year = datetime.datetime.now().year
                year = next_task_date.year
                month = date_str[3:]
                day = date_str[:2]
                formatted_date_str = f"{year}-{month}-{day}"
                try:
                    # Попытка преобразования даты
                    date = pd.Timestamp(formatted_date_str)
                except ValueError as e:
                    if month == "02" and day == "29":
                        continue
                    # Обработка ошибки и вывод строки, которую не удалось преобразовать
                    err_text = f"""Ошибка преобразования даты: {formatted_date_str}
Строка тайминга: {line}
Подробности ошибки: {e}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
                    print(err_text)
                    if month != "02" or day != "29":
                        self.logger.log(err_text)
                    date = pd.Timestamp.now()

                if date < (next_task_date - pd.DateOffset(months=5)):
                    date = date + pd.DateOffset(years=1)
                elif date > (next_task_date + pd.DateOffset(months=5)):
                    date = date - pd.DateOffset(years=1)
                timings[date].append(stage)

        return dict(timings)


class Task:
    def __init__(
        self,
        brand,
        format_,
        project_name,
        customer,
        designer,
        raw_timing,
        status,
        color,
        color_status,
        name,
        task_id,
        parser=None,
        next_task_date=None,
    ):
        self.brand = _normalize_text(brand)
        self.format_ = _normalize_text(format_)
        self.project_name = _normalize_text(project_name)
        self.customer = _normalize_text(customer)
        self.designer = _normalize_text(designer)
        self.raw_timing = _normalize_text(raw_timing, strip=False)
        self.timing_cache = None
        self.status = _normalize_text(status)
        self.color = color
        self.color_status = _normalize_text(color_status)
        self.name = _normalize_text(name)
        self.id = task_id
        self.parser = parser or TimingParser()
        self.next_task_date = next_task_date

    def __repr__(self):
        return f"{self.id} {self.name}"

    @property
    def timing(self):
        if self.timing_cache:
            return self.timing_cache
        else:
            self.timing_cache = self.parser.parse(self.raw_timing, self.next_task_date)
            return self.timing_cache

    @property
    def max_date(self):
        return max(self.timing.keys()) if self.timing else None

    @property
    def min_date(self):
        return min(self.timing.keys()) if self.timing else None

    @property
    def max(self):
        return self.max_date

    @property
    def min(self):
        return self.min_date


# 2. Репозитории
# Определим интерфейсы и базовую реализацию:


class TaskRepository(ABC):
    """Репозиторий для работы с задачами"""

    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        pass


def _determine_status_from_color(color):
    """Определить статус по цвету"""
    cs = COLOR_STATUS
    try:
        color_status = cs.get(color, "work")
    except:
        print("error in convert color: ", color, "\n set it to WORK")
        color_status = "work"
    return color_status


class GoogleSheetsTaskRepository(TaskRepository):
    """Репозиторий для работы с задачами в Google Таблицах"""

    def __init__(
        self,
        sheet_info: GoogleSheetInfo,
        service: GoogleSheetsService,
        source_sheet_info: GoogleSheetInfo = None,
    ):
        # sheet_info is used as target for writes by managers.
        self.sheet_info = sheet_info
        # source_sheet_info is used for reads from main table.
        self.source_sheet_info = source_sheet_info or sheet_info
        self.service = service
        self.df = None
        self.replace_names = REPLACE_NAMES
        self.tasks = dict()
        self.row_issues: List[RowValidationIssue] = []
        self.timing_parser = TimingParser()
        self.dop = {}

    def get_all_tasks(self) -> List[Task]:
        """Получить все задачи"""
        self._load()
        return [task for task in self.tasks.values()]

    def get_tasks_by_date(self, date):
        """Получить задачи по дате"""
        self._load()
        tasks = self.get_task_by_color_status(["work"])
        return [task for task in tasks if date in task.timing.keys()]

    def get_task_by(self, column_name, value):
        """Получить задачи по значению в колонке"""
        ids = self._filter(column_name, value)["id"]
        return self.get_task_by_id(ids)

    def get_task_by_id(self, task_ids):
        """Получить задачи по идентификатору."""
        self._load()
        if isinstance(task_ids, Iterable):
            return [self.tasks[task_id] for task_id in task_ids]
        else:
            return self.tasks[task_ids]

    def get_task_by_color_status(self, color_status):
        """Получить задачи по цветовому статусу."""
        return self.get_task_by("color_status", color_status)

    def _load_and_process_data(self):
        """Загрузить и обработать данные из Google Таблицы."""
        spreadsheet_name = self.source_sheet_info.spreadsheet_name
        sheet_name = self.source_sheet_info.get_sheet_name("tasks")
        assistant_sheet_name = self.source_sheet_info.get_sheet_name("assistant")
        df = self.service.get_dataframe(spreadsheet_name, sheet_name)
        self._validate_required_columns(df, spreadsheet_name, sheet_name)
        color_range = f"A2:A{len(df) + 1}"
        colors = self.service.get_cell_colors(spreadsheet_name, sheet_name, color_range)
        # в ячейке ДИЗАЙНЕР может быть несколько человек, там str в котором на каждой строчке один человек
        # надо эти строчки отсортировать по алфавиту удалив лишние пробелы в начале и конце каждоый строки
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].fillna("")
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].apply(
            lambda x: "\n".join(sorted([i.strip() for i in x.split("\n") if i.strip()]))
        )
        df["ДИЗАЙНЕР"] = df["ДИЗАЙНЕР"].apply(lambda x: "[Не назначен]" if x == "" else x)
        df["color"] = colors
        df["color_status"] = df["color"].apply(_determine_status_from_color)
        df["id"] = df.index + 2
        df["name"] = df.apply(self._generate_task_name, axis=1)

        self.dop = {
            "assiatant_main_prompt": self.service.get_dataframe(
                spreadsheet_name, assistant_sheet_name, worksheet_range="F3:F4", header=False
            ).at[0, 0],
            "assistant_model": self.service.get_dataframe(
                spreadsheet_name, assistant_sheet_name, worksheet_range="E3:E4", header=False
            ).at[0, 0],
            "assistant_advice": self.service.get_dataframe(
                spreadsheet_name, assistant_sheet_name, worksheet_range="B3:B1000", header=False
            ),
        }

        self.df = df
        self._df_to_task(df)

    def _validate_required_columns(self, df, spreadsheet_name, sheet_name):
        required_columns = TaskRowContract.required_columns(TASK_FIELD_MAP)
        missing = sorted(col for col in required_columns if col not in df.columns)
        if missing:
            raise MissingRequiredColumnsError(
                entity_name="task",
                spreadsheet_name=spreadsheet_name,
                sheet_name=sheet_name,
                missing_columns=tuple(missing),
                field_map_name="TASK_FIELD_MAP",
            )

    def _generate_task_name(self, row):
        """Сгенерировать название задачи"""
        raw_format = row.get("ФОРМАТ", "")
        raw_format = "" if pd.isna(raw_format) else str(raw_format)
        format_ = raw_format.split("\n")[0] if raw_format else ""
        brand = "" if pd.isna(row.get("БРЕНД")) else str(row.get("БРЕНД"))
        project = "" if pd.isna(row.get("ПРОЕКТ")) else str(row.get("ПРОЕКТ"))
        name = f"{brand} [{project}] {format_}".strip()
        for key, value in self.replace_names.items():
            name = name.replace(key, value)
        return name

    def _load(self):
        """Проверить наличие данных"""
        if self.df is None:
            self._load_and_process_data()

    def _df_to_task(self, df):
        """Преобразовать DataFrame в список задач"""
        self.row_issues = []
        tasks_list = []
        next_task_date = None
        for idx, row in df.iterrows():
            row_number = int(idx) + 2
            try:
                contract = TaskRowContract.from_mapping(row, TASK_FIELD_MAP)
                task = Task(
                    **contract.to_task_kwargs(),
                    parser=self.timing_parser,
                    next_task_date=next_task_date,
                )
            except (TypeError, ValueError, KeyError) as exc:
                self._record_row_issue("task", row_number, f"mapping failure: {exc}")
                continue
            if _is_nullish(task.id):
                self._record_row_issue("task", row_number, "missing task id")
                continue
            if task.id in self.tasks:
                self._record_row_issue("task", row_number, "duplicate task id", row_id=str(task.id))
                continue
            tasks_list.append(task)
            self.tasks[task.id] = task
            mean_date = pd.Series(task.timing.keys()).mean()
            if not pd.isna(mean_date):
                next_task_date = mean_date
        return tasks_list

    def _record_row_issue(self, entity_name: str, row_number: int, reason: str, row_id: str = ""):
        issue = RowValidationIssue(
            entity_name=entity_name,
            row_number=row_number,
            reason=reason,
            row_id=row_id,
        )
        self.row_issues.append(issue)
        print(str(issue))

    def _filter(self, column_name, value):
        """Отфильтровать DataFrame по значению в колонке"""
        self._load()
        # если не кортеж или список, то преобразуем в список
        if not isinstance(value, Iterable):
            value = [value]
        return self.df[self.df[column_name].isin(value)]

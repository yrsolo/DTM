"""
Модуль содержит класс GoogleSheetPlanner, предоставляющий высокоуровневый интерфейс
для работы с задачами и календарем в Google Sheets. Этот класс интегрирует различные
компоненты системы, такие как управление задачами, управление календарем и
сервисные функции для работы с Google Sheets.
"""

from utils.service import GoogleSheetsService, GoogleSheetInfo
from core.manager import TaskTimingProcessor, CalendarManager, TaskManager, TaskCalendarManager
from core.repository import GoogleSheetsTaskRepository
from core.reminder import Reminder, AsyncOpenAIChatAgent
from core.people import PeopleManager
from config import HELPER_CHARACTER, TG, OPENAI, ORG, PROXIES, MODEL


class GoogleSheetPlanner:
    def __init__(self, key_json, sheet_info_data, mode='test'):
        self.mode = mode
        self.sheet_info = GoogleSheetInfo(**sheet_info_data)
        self.service = GoogleSheetsService(key_json)
        self.timing_processor = TaskTimingProcessor()
        self.task_repository = GoogleSheetsTaskRepository(self.sheet_info, self.service)
        self.task_manager = TaskManager(self.task_repository)
        self.calendar_manager = CalendarManager(self.sheet_info, self.service, self.task_repository)
        self.task_calendar_manager = TaskCalendarManager(self.sheet_info, self.service, self.task_repository)
        self.openai_agent = AsyncOpenAIChatAgent(api_key=OPENAI, organization=ORG, proxies=PROXIES, model=MODEL)
        self.people_manager = PeopleManager(service=self.service, sheet_info=self.sheet_info)
        self.reminder = Reminder(self.task_repository, self.openai_agent, HELPER_CHARACTER,
                                 tg_bot_token=TG, people_manager=self.people_manager)

    def task_to_table(self, color_status=('work', 'pre_done')):
        self.task_manager.task_to_table(color_status)

    def designer_task_to_calendar(self, color_status=('work', 'pre_done'), min_date='1W'):
        tasks = self.task_repository.get_task_by_color_status(color_status)
        task_timings = self.timing_processor.create_task_timing_structure(tasks)
        calendar = self.calendar_manager.create_calendar_structure(task_timings)
        self.calendar_manager.write_calendar_to_sheet(calendar, min_date)

    def update(self):
        return self.task_manager.update()

    def task_to_calendar(self, color_status=('wait', 'work', 'pre_done')):
        tasks = self.task_repository.get_task_by_color_status(color_status)
        task_timings = self.timing_processor.create_task_timing_structure(tasks)
        calendar = self.task_calendar_manager.create_task_calendar_structure(task_timings)
        self.task_calendar_manager.write_task_calendar_to_sheet(calendar)

    async def send_reminders(self):
        await self.reminder.get_reminders()
        await self.reminder.send_reminders(mode=self.mode)

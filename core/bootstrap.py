"""Stage 2 bootstrap boundary for planner dependency wiring."""

from dataclasses import dataclass

from config import HELPER_CHARACTER, MODEL, OPENAI, ORG, PROXIES, SOURCE_SHEET_INFO, TG
from core.manager import CalendarManager, TaskCalendarManager, TaskManager, TaskTimingProcessor
from core.people import PeopleManager
from core.reminder import AsyncOpenAIChatAgent, MockOpenAIChatAgent, Reminder
from core.repository import GoogleSheetsTaskRepository
from utils.service import GoogleSheetInfo, GoogleSheetsService


@dataclass
class PlannerDependencies:
    service: GoogleSheetsService
    timing_processor: TaskTimingProcessor
    task_repository: GoogleSheetsTaskRepository
    task_manager: TaskManager
    calendar_manager: CalendarManager
    task_calendar_manager: TaskCalendarManager
    openai_agent: object
    people_manager: PeopleManager
    reminder: Reminder


def build_planner_dependencies(
        key_json,
        sheet_info_data,
        dry_run=False,
        mock_external=False,
):
    sheet_info = GoogleSheetInfo(**sheet_info_data)
    source_sheet_info = GoogleSheetInfo(**SOURCE_SHEET_INFO)

    service = GoogleSheetsService(key_json, dry_run=dry_run)
    timing_processor = TaskTimingProcessor()
    task_repository = GoogleSheetsTaskRepository(
        sheet_info,
        service,
        source_sheet_info=source_sheet_info,
    )
    task_manager = TaskManager(task_repository)
    calendar_manager = CalendarManager(sheet_info, service, task_repository)
    task_calendar_manager = TaskCalendarManager(sheet_info, service, task_repository)

    openai_agent = (
        MockOpenAIChatAgent()
        if mock_external
        else AsyncOpenAIChatAgent(
            api_key=OPENAI,
            organization=ORG,
            proxies=PROXIES,
            model=MODEL,
        )
    )
    people_manager = PeopleManager(service=service, sheet_info=source_sheet_info)
    reminder = Reminder(
        task_repository,
        openai_agent,
        HELPER_CHARACTER,
        tg_bot_token=TG,
        people_manager=people_manager,
        mock_openai=mock_external,
        mock_telegram=mock_external,
    )

    return PlannerDependencies(
        service=service,
        timing_processor=timing_processor,
        task_repository=task_repository,
        task_manager=task_manager,
        calendar_manager=calendar_manager,
        task_calendar_manager=task_calendar_manager,
        openai_agent=openai_agent,
        people_manager=people_manager,
        reminder=reminder,
    )

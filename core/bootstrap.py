"""Stage 2 bootstrap boundary for planner dependency wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from config import HELPER_CHARACTER, MODEL, OPENAI, ORG, PROXIES, SOURCE_SHEET_INFO, TG
from core.adapters import ChatAdapter, MessageAdapter, SheetRenderAdapter
from core.manager import CalendarManager, TaskCalendarManager, TaskManager, TaskTimingProcessor
from core.people import PeopleManager
from core.reminder import AsyncOpenAIChatAgent, MockOpenAIChatAgent, Reminder, TelegramNotifier
from core.repository import GoogleSheetsTaskRepository
from core.sheet_renderer import ServiceSheetRenderAdapter
from utils.service import GoogleSheetInfo, GoogleSheetsService


@dataclass
class PlannerDependencies:
    service: GoogleSheetsService
    timing_processor: TaskTimingProcessor
    task_repository: GoogleSheetsTaskRepository
    task_manager: TaskManager
    designers_renderer: SheetRenderAdapter
    calendar_manager: CalendarManager
    calendar_renderer: SheetRenderAdapter
    task_calendar_manager: TaskCalendarManager
    task_calendar_renderer: SheetRenderAdapter
    openai_agent: ChatAdapter
    telegram_adapter: MessageAdapter | None
    people_manager: PeopleManager
    reminder: Reminder


def build_planner_dependencies(
    key_json: str,
    sheet_info_data: Mapping[str, str],
    dry_run: bool = False,
    mock_external: bool = False,
) -> PlannerDependencies:
    """Construct runtime dependencies for planner orchestration."""
    sheet_info = GoogleSheetInfo(**sheet_info_data)
    source_sheet_info = GoogleSheetInfo(**SOURCE_SHEET_INFO)

    service = GoogleSheetsService(key_json, dry_run=dry_run)
    timing_processor = TaskTimingProcessor()
    task_repository = GoogleSheetsTaskRepository(
        sheet_info,
        service,
        source_sheet_info=source_sheet_info,
    )
    designers_renderer: SheetRenderAdapter = ServiceSheetRenderAdapter(
        service=service,
        spreadsheet_name=sheet_info.spreadsheet_name,
        sheet_name=sheet_info.get_sheet_name("designers"),
    )
    task_manager = TaskManager(
        task_repository,
        renderer=designers_renderer,
    )
    calendar_renderer: SheetRenderAdapter = ServiceSheetRenderAdapter(
        service=service,
        spreadsheet_name=sheet_info.spreadsheet_name,
        sheet_name=sheet_info.get_sheet_name("calendar"),
    )
    calendar_manager = CalendarManager(
        sheet_info,
        service,
        task_repository,
        renderer=calendar_renderer,
    )
    task_calendar_renderer: SheetRenderAdapter = ServiceSheetRenderAdapter(
        service=service,
        spreadsheet_name=sheet_info.spreadsheet_name,
        sheet_name=sheet_info.get_sheet_name("task_calendar"),
    )
    task_calendar_manager = TaskCalendarManager(
        sheet_info,
        service,
        task_repository,
        renderer=task_calendar_renderer,
    )

    openai_agent: ChatAdapter = (
        MockOpenAIChatAgent()
        if mock_external
        else AsyncOpenAIChatAgent(
            api_key=OPENAI,
            organization=ORG,
            proxies=PROXIES,
            model=MODEL,
        )
    )
    telegram_adapter: MessageAdapter | None = None if mock_external else TelegramNotifier(TG)
    people_manager = PeopleManager(service=service, sheet_info=source_sheet_info)
    reminder = Reminder(
        task_repository,
        openai_agent,
        HELPER_CHARACTER,
        tg_bot_token=TG,
        people_manager=people_manager,
        mock_openai=mock_external,
        mock_telegram=mock_external,
        telegram_adapter=telegram_adapter,
    )

    return PlannerDependencies(
        service=service,
        timing_processor=timing_processor,
        task_repository=task_repository,
        task_manager=task_manager,
        designers_renderer=designers_renderer,
        calendar_manager=calendar_manager,
        calendar_renderer=calendar_renderer,
        task_calendar_manager=task_calendar_manager,
        task_calendar_renderer=task_calendar_renderer,
        openai_agent=openai_agent,
        telegram_adapter=telegram_adapter,
        people_manager=people_manager,
        reminder=reminder,
    )

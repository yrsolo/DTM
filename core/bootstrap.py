"""Stage 2 bootstrap boundary for planner dependency wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from config import (
    GOOGLE_LLM_API_KEY,
    GOOGLE_LLM_MODEL,
    HELPER_CHARACTER,
    LLM_PROVIDER,
    MODEL,
    OPENAI,
    ORG,
    PROXIES,
    SOURCE_SHEET_INFO,
    TG,
    YANDEX_LLM_API_KEY,
    YANDEX_LLM_MODEL_URI,
)
from core.adapters import ChatAdapter, MessageAdapter, SheetRenderAdapter
from core.manager import CalendarManager, TaskCalendarManager, TaskManager, TaskTimingProcessor
from core.people import PeopleManager
from core.reminder import (
    AsyncGoogleLLMChatAgent,
    AsyncOpenAIChatAgent,
    AsyncYandexLLMChatAgent,
    MockOpenAIChatAgent,
    Reminder,
    TelegramNotifier,
)
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


def _build_renderer(
    service: GoogleSheetsService,
    sheet_info: GoogleSheetInfo,
    sheet_key: str,
) -> SheetRenderAdapter:
    """Create typed sheet renderer bound to target sheet key."""

    return ServiceSheetRenderAdapter(
        service=service,
        spreadsheet_name=sheet_info.spreadsheet_name,
        sheet_name=sheet_info.get_sheet_name(sheet_key),
    )


def _build_chat_adapter(mock_external: bool) -> ChatAdapter:
    """Create chat adapter according to selected provider and runtime mode."""

    if mock_external:
        return MockOpenAIChatAgent()

    provider = LLM_PROVIDER.lower()
    if provider == "openai":
        return AsyncOpenAIChatAgent(
            api_key=OPENAI,
            organization=ORG,
            proxies=PROXIES,
            model=MODEL,
        )
    if provider == "google":
        return AsyncGoogleLLMChatAgent(
            api_key=GOOGLE_LLM_API_KEY,
            model=GOOGLE_LLM_MODEL,
        )
    if provider == "yandex":
        return AsyncYandexLLMChatAgent(
            api_key=YANDEX_LLM_API_KEY,
            model_uri=YANDEX_LLM_MODEL_URI,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER={provider!r}. Allowed values: openai, google, yandex."
    )


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
    task_repository = GoogleSheetsTaskRepository(
        sheet_info,
        service,
        source_sheet_info=source_sheet_info,
    )
    timing_processor = TaskTimingProcessor()

    designers_renderer = _build_renderer(service, sheet_info, "designers")
    calendar_renderer = _build_renderer(service, sheet_info, "calendar")
    task_calendar_renderer = _build_renderer(service, sheet_info, "task_calendar")

    task_manager = TaskManager(task_repository, renderer=designers_renderer)
    calendar_manager = CalendarManager(
        sheet_info,
        service,
        task_repository,
        renderer=calendar_renderer,
    )
    task_calendar_manager = TaskCalendarManager(
        sheet_info,
        service,
        task_repository,
        renderer=task_calendar_renderer,
    )

    openai_agent = _build_chat_adapter(mock_external)
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

"""DEPRECATED: reference-only legacy planner bootstrap wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

from config import (
    GOOGLE_LLM_API_KEY,
    OPENAI,
    ORG,
    PROXIES,
    TG,
    YANDEX_LLM_API_KEY,
    YANDEX_LLM_MODEL_URI,
)
from core.adapters import ChatAdapter, MessageAdapter, SheetRenderAdapter
from core.reminder import (
    AsyncGoogleLLMChatAgent,
    AsyncOpenAIChatAgent,
    AsyncYandexLLMChatAgent,
    FallbackChatAdapter,
    MockOpenAIChatAgent,
    Reminder,
    TelegramNotifier,
)
from src.adapters.google_sheets.people_manager import PeopleManager
from src.adapters.google_sheets.task_repository import GoogleSheetsTaskRepository
from core.sheet_renderer import ServiceSheetRenderAdapter
from src.config.loader import load_config
from core.task_timing_processor import TaskTimingProcessor
from src.archive.legacy_runtime.services.calendar_runtime import CalendarManager, TaskCalendarManager
from src.archive.legacy_runtime.services.render.task_table_runtime import TaskManager

if TYPE_CHECKING:
    from src.config.schema import AppConfig
    from utils.service import GoogleSheetInfo, GoogleSheetsService

# Backward-compatible mutable knobs for legacy shim consumers (`core/bootstrap.py`).
_LEGACY_CFG = load_config()
LLM_PROVIDER = str(_LEGACY_CFG.llm.llm.get("provider_default", "openai"))
LLM_FAILOVER_MODE = str(_LEGACY_CFG.llm.failover.get("mode_default", "draft_only"))
LLM_FAILOVER_PROVIDER = str(_LEGACY_CFG.llm.failover.get("provider_default", ""))


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
    return ServiceSheetRenderAdapter(
        service=service,
        spreadsheet_name=sheet_info.spreadsheet_name,
        sheet_name=sheet_info.get_sheet_name(sheet_key),
    )


def _build_single_chat_adapter(
    provider: str,
    *,
    openai_model: str,
    google_model: str,
    yandex_model_uri: str,
    timeout_seconds: float,
    retry_attempts: int,
    retry_backoff_seconds: float,
) -> ChatAdapter:
    provider = str(provider or "").lower()
    if provider == "openai":
        return AsyncOpenAIChatAgent(
            api_key=OPENAI,
            organization=ORG,
            proxies=PROXIES,
            model=openai_model,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff_seconds,
        )
    if provider == "google":
        return AsyncGoogleLLMChatAgent(
            api_key=GOOGLE_LLM_API_KEY,
            model=google_model,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff_seconds,
        )
    if provider == "yandex":
        return AsyncYandexLLMChatAgent(
            api_key=YANDEX_LLM_API_KEY,
            model_uri=yandex_model_uri,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff_seconds,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER={provider!r}. Allowed values: openai, google, yandex."
    )


def _build_chat_adapter(
    mock_external: bool,
    *,
    provider: str | None = None,
    openai_model: str | None = None,
    google_model: str | None = None,
    yandex_model_uri: str | None = None,
    timeout_seconds: float | None = None,
    retry_attempts: int | None = None,
    retry_backoff_seconds: float | None = None,
    failover_mode: str | None = None,
    failover_provider: str | None = None,
) -> ChatAdapter:
    if mock_external:
        return MockOpenAIChatAgent()

    cfg = load_config()
    provider = str(provider or LLM_PROVIDER or cfg.llm.llm.get("provider_default", "openai")).lower()
    openai_model = str(openai_model or cfg.llm.models.get("openai_default", "gpt-4o"))
    google_model = str(google_model or cfg.llm.models.get("google_default", "gemini-2.0-flash"))
    yandex_model_uri = str(
        yandex_model_uri or cfg.llm.models.get("yandex_default_uri", YANDEX_LLM_MODEL_URI)
    )
    timeout_seconds = float(timeout_seconds or cfg.llm.http.get("timeout_seconds", 25))
    retry_attempts = int(retry_attempts or cfg.llm.http.get("retry_attempts", 2))
    retry_backoff_seconds = float(
        retry_backoff_seconds or cfg.llm.http.get("retry_backoff_seconds", 0.8)
    )
    primary = _build_single_chat_adapter(
        provider,
        openai_model=openai_model,
        google_model=google_model,
        yandex_model_uri=yandex_model_uri,
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    failover_mode = str(
        failover_mode or LLM_FAILOVER_MODE or cfg.llm.failover.get("mode_default", "draft_only")
    ).lower()
    failover_provider = str(
        failover_provider or LLM_FAILOVER_PROVIDER or cfg.llm.failover.get("provider_default", "")
    ).lower()
    if failover_mode != "provider":
        return FallbackChatAdapter(
            primary=primary,
            primary_provider=provider,
            mode=failover_mode,
            fallback=None,
            fallback_provider="",
        )

    if not failover_provider:
        return FallbackChatAdapter(
            primary=primary,
            primary_provider=provider,
            mode="draft_only",
            fallback=None,
            fallback_provider="",
        )
    if failover_provider == provider:
        return FallbackChatAdapter(
            primary=primary,
            primary_provider=provider,
            mode="draft_only",
            fallback=None,
            fallback_provider="",
        )
    fallback = _build_single_chat_adapter(
        failover_provider,
        openai_model=openai_model,
        google_model=google_model,
        yandex_model_uri=yandex_model_uri,
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    return FallbackChatAdapter(
        primary=primary,
        primary_provider=provider,
        mode="provider",
        fallback=fallback,
        fallback_provider=failover_provider,
    )


def build_planner_dependencies(
    key_json: str,
    sheet_info_data: Mapping[str, str],
    dry_run: bool = False,
    mock_external: bool = False,
    cfg: AppConfig | None = None,
) -> PlannerDependencies:
    from utils.service import GoogleSheetInfo, GoogleSheetsService

    if cfg is None:
        cfg = load_config()

    source_sheet_name = str(cfg.tables.google_sheets.get("source_sheet_name_default", "")).strip()
    source_sheet_info_data = {
        "spreadsheet_name": source_sheet_name,
        "sheet_names": dict(cfg.tables.sheet_names),
    }

    llm_provider = str(cfg.llm.llm.get("provider_default", "openai"))
    openai_model = str(cfg.llm.models.get("openai_default", "gpt-4o"))
    google_model = str(cfg.llm.models.get("google_default", "gemini-2.0-flash"))
    yandex_model_uri = YANDEX_LLM_MODEL_URI
    yandex_model_uri = str(cfg.llm.models.get("yandex_default_uri", yandex_model_uri))
    llm_http_timeout_seconds = float(cfg.llm.http.get("timeout_seconds", 25))
    llm_http_retry_attempts = int(cfg.llm.http.get("retry_attempts", 2))
    llm_http_retry_backoff_seconds = float(cfg.llm.http.get("retry_backoff_seconds", 0.8))
    llm_failover_mode = str(cfg.llm.failover.get("mode_default", "draft_only"))
    llm_failover_provider = str(cfg.llm.failover.get("provider_default", ""))
    helper_character = str(cfg.llm.assistant.get("helper_character", ""))
    color_palette = dict(cfg.mapping.palette)
    timing_year_mode = str(cfg.runtime.timing.year_mode_default or "legacy")
    task_field_map = dict(cfg.tables.field_maps.get("tasks", {}))
    people_field_map = dict(cfg.tables.field_maps.get("people", {}))
    color_status_map = dict(cfg.mapping.status_by_color)
    replace_names = dict(cfg.mapping.project_aliases)

    sheet_info = GoogleSheetInfo(**sheet_info_data)
    source_sheet_info = GoogleSheetInfo(**source_sheet_info_data)

    service = GoogleSheetsService(key_json, dry_run=dry_run)
    task_repository = GoogleSheetsTaskRepository(
        sheet_info,
        service,
        source_sheet_info=source_sheet_info,
        timing_year_mode=timing_year_mode,
        task_field_map=task_field_map,
        replace_names=replace_names,
        color_status_map=color_status_map,
    )
    timing_processor = TaskTimingProcessor(timing_year_mode=timing_year_mode)

    designers_renderer = _build_renderer(service, sheet_info, "designers")
    calendar_renderer = _build_renderer(service, sheet_info, "calendar")
    task_calendar_renderer = _build_renderer(service, sheet_info, "task_calendar")

    task_manager = TaskManager(task_repository, renderer=designers_renderer)
    calendar_manager = CalendarManager(
        sheet_info,
        service,
        task_repository,
        renderer=calendar_renderer,
        palette=color_palette,
    )
    task_calendar_manager = TaskCalendarManager(
        sheet_info,
        service,
        task_repository,
        renderer=task_calendar_renderer,
        palette=color_palette,
    )

    openai_agent = _build_chat_adapter(
        mock_external,
        provider=llm_provider,
        openai_model=openai_model,
        google_model=google_model,
        yandex_model_uri=yandex_model_uri,
        timeout_seconds=llm_http_timeout_seconds,
        retry_attempts=llm_http_retry_attempts,
        retry_backoff_seconds=llm_http_retry_backoff_seconds,
        failover_mode=llm_failover_mode,
        failover_provider=llm_failover_provider,
    )
    telegram_adapter: MessageAdapter | None = None if mock_external else TelegramNotifier(TG)
    people_manager = PeopleManager(
        service=service,
        sheet_info=source_sheet_info,
        people_field_map=people_field_map,
    )
    reminder = Reminder(
        task_repository,
        openai_agent,
        helper_character,
        tg_bot_token=TG,
        people_manager=people_manager,
        mock_openai=mock_external,
        mock_telegram=mock_external,
        telegram_adapter=telegram_adapter,
        llm_provider_name=llm_provider,
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

"""Shared runtime entry for planner modes used by jobs and HTTP entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from src.adapters.telegram import TelegramNotifier
from src.adapters.llm_google import AsyncGoogleLLMChatAgent
from src.adapters.llm_openai import AsyncOpenAIChatAgent
from src.adapters.llm_yandex import AsyncYandexLLMChatAgent
from src.app.bootstrap import build_app_context
from src.entrypoints.jobs.db_migrate_branch import run_db_migrate_if_requested
from src.entrypoints.jobs.db_migrate_job import run_db_migrate
from src.entrypoints.jobs.quality_report_job import print_quality_report as _print_quality_report
from src.entrypoints.jobs.runtime_context_job import RuntimeContextRequest, resolve_runtime_context
from src.entrypoints.jobs.timer_job import TimerJob
from src.notify import ReminderFormatter, ReminderJob, ReminderRequest, ReminderUseCase
from src.render import (
    DesignersRenderUseCase,
    GoogleSheetsPlanWriter,
    RenderJob,
    RenderRequest,
    RenderUseCase,
    SheetTarget,
)
from src.render.target_guard import RenderTarget, validate_render_target
from src.services.sources.sheets_normalized_source import build_sheets_normalized_task_source
from src.snapshot_engine import build_snapshot_engine
from src.snapshot_engine.model import Window
from src.services.timer_pipeline import RunRequest as TimerRunRequest
from src.services.timer_pipeline import TimerPipeline
from src.entrypoints.runtime.runtime_contract import STANDARD_RUN_MODES, is_legacy_mode

APP_CONTEXT = build_app_context()
APP_DEPS = APP_CONTEXT.deps
PIPELINE_CFG = APP_CONTEXT.cfg.runtime.pipeline
APP_RUNTIME_ENV = APP_CONTEXT.cfg.runtime.runtime.env_default
APP_STORE_MODE = APP_CONTEXT.cfg.runtime.sources.store_mode_default
APP_TRIGGERS = APP_CONTEXT.cfg.runtime.triggers
APP_KEY_JSON = str(APP_DEPS.get("key_json", ""))
APP_SHEET_INFO = dict(APP_DEPS.get("sheet_info", {}))
APP_YDB_ENDPOINT = str(APP_DEPS.get("ydb_endpoint", ""))
APP_YDB_DATABASE = str(APP_DEPS.get("ydb_database", ""))
APP_YDB_SA_JSON_CREDENTIALS = APP_DEPS.get("ydb_sa_json_credentials")
APP_YDB_SA_KEY_FILE = APP_DEPS.get("ydb_sa_key_file")
APP_LEGACY_BLOB_WRITE = bool(APP_DEPS.get("legacy_blob_write", False))
APP_MIGRATION_STORE_FILE = str(APP_DEPS.get("migration_store_file", "store.json"))
APP_YDB_MIGRATE_ON_START = bool(APP_DEPS.get("ydb_migrate_on_start", False))
TIMER_JOB_SHELL = TimerJob()


def _resolve_standard_run_mode(
    mode: str | None = None,
    event: Any = None,
    triggers: dict[str, str] | None = None,
) -> str:
    if mode:
        return str(mode).strip().lower()
    if event == "morning":
        return "morning"
    if isinstance(event, dict):
        try:
            trigger_id = str(event["messages"][0]["details"]["trigger_id"]).strip()
        except (TypeError, KeyError, IndexError):
            trigger_id = ""
        if trigger_id:
            return str((triggers or {}).get(trigger_id, "test")).strip().lower()
    return "test"


def _build_notify_enhancer(mock_external: bool):
    if bool(mock_external):
        return None
    cfg = APP_CONTEXT.cfg
    provider = str(cfg.llm.llm.get("provider_default", "openai")).strip().lower()
    model_openai = str(cfg.llm.models.get("openai_default", "")).strip()
    model_google = str(cfg.llm.models.get("google_default", "")).strip()
    model_yandex = str(cfg.llm.models.get("yandex_default_uri", "")).strip()
    timeout = float(cfg.llm.http.get("timeout_seconds_default", 25))
    retry_attempts = int(cfg.llm.http.get("retry_attempts_default", 2))
    retry_backoff = float(cfg.llm.http.get("retry_backoff_seconds_default", 0.8))
    proxy_url = str(APP_DEPS.get("proxy_url", "")).strip()
    proxy_map = {"https://": proxy_url, "http://": proxy_url} if proxy_url else {}
    if provider == "google":
        api_key = str(APP_DEPS.get("google_llm_api_key", "")).strip()
        if not api_key:
            return None
        return AsyncGoogleLLMChatAgent(
            api_key=api_key,
            model=model_google,
            timeout_seconds=timeout,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff,
        )
    if provider == "yandex":
        api_key = str(APP_DEPS.get("yandex_llm_api_key", "")).strip()
        if not api_key or not model_yandex:
            return None
        return AsyncYandexLLMChatAgent(
            api_key=api_key,
            model_uri=model_yandex,
            timeout_seconds=timeout,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff,
        )
    api_key = str(APP_DEPS.get("openai_token", "")).strip()
    if not api_key:
        return None
    return AsyncOpenAIChatAgent(
        api_key=api_key,
        proxies=proxy_map,
        model=model_openai,
        organization=str(APP_DEPS.get("org_token", "")).strip() or None,
        timeout_seconds=timeout,
        retry_attempts=retry_attempts,
        retry_backoff_seconds=retry_backoff,
    )


@dataclass(frozen=True)
class PlannerRuntimeRequest:
    event: Any = None
    mode: str | None = None
    dry_run: bool = False
    mock_external: Any = None
    force_refresh: bool | None = None


async def run_planner_runtime(request: PlannerRuntimeRequest):
    """Run planner runtime mode through shared entry logic."""
    dry_run = request.dry_run
    runtime_ctx = resolve_runtime_context(
        RuntimeContextRequest(
            mode=request.mode,
            event=request.event,
            dry_run=dry_run,
            mock_external=request.mock_external,
            force_refresh_raw=request.force_refresh,
            triggers=APP_TRIGGERS,
            force_refresh_default=PIPELINE_CFG.force_refresh_default,
            resolve_run_mode=_resolve_standard_run_mode,
            timer_job_shell=TIMER_JOB_SHELL,
            app_context=APP_CONTEXT,
        )
    )
    mode = runtime_ctx.mode
    mock_external = runtime_ctx.mock_external
    force_refresh = runtime_ctx.force_refresh

    migrate_handled, migrate_result = run_db_migrate_if_requested(
        mode=mode,
        endpoint=APP_YDB_ENDPOINT,
        database=APP_YDB_DATABASE,
        sa_json_credentials=APP_YDB_SA_JSON_CREDENTIALS,
        sa_key_file=APP_YDB_SA_KEY_FILE,
        run_db_migrate=run_db_migrate,
    )
    if migrate_handled:
        return migrate_result

    task_source = build_sheets_normalized_task_source(
        key_json=APP_KEY_JSON,
        sheet_info_data=APP_SHEET_INFO,
        cfg=APP_CONTEXT.cfg,
        dry_run=dry_run,
    )
    normalized_mode = str(mode).strip().lower()
    if is_legacy_mode(normalized_mode) or normalized_mode not in STANDARD_RUN_MODES:
        return {
            "artifact": "dtm_runtime",
            "status": "unsupported_mode",
            "mode": normalized_mode,
            "supported_modes": sorted(STANDARD_RUN_MODES),
        }
    quality_report: dict[str, Any] = {"summary": {"task_row_issue_count": 0}}

    if normalized_mode in {"reminder_v2", "reminders-only", "morning", "test"}:
        snapshot_engine = build_snapshot_engine(APP_CONTEXT)
        usecase = ReminderUseCase(snapshot_engine)
        formatter = ReminderFormatter(
            timezone_name=str(APP_CONTEXT.cfg.runtime.runtime.timezone or "Europe/Moscow"),
            hidden_stage_names=tuple(APP_CONTEXT.cfg.mapping.hidden_stage_names or ()),
        )
        sender = TelegramNotifier(
            bot_token=str(APP_DEPS.get("tg_bot_token", "")),
            default_chat_id=APP_DEPS.get("default_chat_id"),
        )
        notify_cfg = APP_CONTEXT.cfg.runtime.notify
        llm_mode = str(notify_cfg.llm_mode_default or "provider")
        mock_llm = bool(mock_external or llm_mode == "draft_only" or APP_RUNTIME_ENV == "test")
        enhancer = _build_notify_enhancer(mock_external=mock_llm)
        reminder_result = await ReminderJob(
            usecase=usecase,
            formatter=formatter,
            sender=sender,
            helper_character=str(APP_CONTEXT.cfg.llm.assistant.get("helper_character", "")),
            enhancer=enhancer,
            people_lookup=snapshot_engine,
            default_chat_id=str(APP_DEPS.get("default_chat_id", "")).strip(),
            enhance_concurrency=int(notify_cfg.enhance_concurrency),
            send_retry_attempts=int(notify_cfg.send_retry_attempts),
            send_retry_backoff_seconds=float(notify_cfg.send_retry_backoff_seconds),
            send_retry_backoff_multiplier=float(notify_cfg.send_retry_backoff_multiplier),
            llm_mode=llm_mode,
            llm_model=str(APP_CONTEXT.cfg.llm.models.get("openai_default", "")),
            runtime_env=APP_RUNTIME_ENV,
            mock_llm=mock_llm,
        ).run(
            ReminderRequest(
                mode=normalized_mode,
                statuses=["work", "pre_done"],
                include_today=True,
                include_next_workday=True,
                force_test_chat=(APP_RUNTIME_ENV == "test" or normalized_mode == "test"),
                test_chat_id_override=str(notify_cfg.test_chat_id_override or ""),
            )
        )
        if normalized_mode in {"reminder_v2", "reminders-only", "morning"}:
            return {
                "artifact": reminder_result.artifact,
                "status": reminder_result.status,
                "mode": reminder_result.mode,
                "summary": {
                    "task_row_issue_count": 0,
                    "groups": len(reminder_result.groups),
                },
                "delivery_counters": dict(reminder_result.delivery_counters),
                "enhancement_counters": dict(reminder_result.enhancement_counters),
                "warnings": list(reminder_result.warnings),
                "today": reminder_result.today,
                "next_workday": reminder_result.next_workday,
            }

    TimerPipeline(APP_CONTEXT).run(
        TimerRunRequest(
            mode=mode,
            force_refresh=force_refresh,
            task_source=task_source,
        )
    )

    if normalized_mode in {"timer", "test", "render_v2"}:
        render_started = perf_counter()
        snapshot_engine = build_snapshot_engine(APP_CONTEXT)
        render_usecase = RenderUseCase(
            snapshot_engine,
            timezone_name=str(APP_CONTEXT.cfg.runtime.runtime.timezone or "Europe/Moscow"),
        )
        from utils.service import GoogleSheetInfo, GoogleSheetsService

        sheet_info = GoogleSheetInfo(**APP_SHEET_INFO)
        target_worksheet = sheet_info.get_sheet_name("task_calendar") or "Задачи"
        source_spreadsheet = str(
            APP_CONTEXT.cfg.tables.google_sheets.get("source_sheet_name_default", "")
        ).strip()
        target_spreadsheet = str(sheet_info.spreadsheet_name or "").strip()
        tasks_sheet_name = str(sheet_info.get_sheet_name("tasks") or "ТАБЛИЧКА").strip()
        target_ok, target_warnings = validate_render_target(
            RenderTarget(
                source_spreadsheet=source_spreadsheet,
                target_spreadsheet=target_spreadsheet,
                tasks_sheet_name=tasks_sheet_name,
                target_worksheet=str(target_worksheet),
            )
        )
        if not target_ok:
            return {
                "artifact": "render_v2",
                "status": "blocked",
                "mode": "render_v2",
                "render_applied": False,
                "rows_written": 0,
                "cells_written": 0,
                "target_spreadsheet": target_spreadsheet,
                "target_worksheet": target_worksheet,
                "warnings": list(target_warnings),
                "error": {
                    "code": "render_target_unsafe",
                    "details": {
                        "source_spreadsheet": source_spreadsheet,
                        "target_spreadsheet": target_spreadsheet,
                        "target_worksheet": target_worksheet,
                        "tasks_sheet_name": tasks_sheet_name,
                    },
                },
                "duration_ms": int((perf_counter() - render_started) * 1000),
                "summary": {"task_row_issue_count": 0},
            }
        writer = GoogleSheetsPlanWriter(
            GoogleSheetsService(APP_KEY_JSON, dry_run=dry_run),
            SheetTarget(
                spreadsheet_name=sheet_info.spreadsheet_name,
                worksheet_name=target_worksheet,
            ),
        )
        render_result = RenderJob(render_usecase, writer).run(
            RenderRequest(
                window=Window(start=None, end=None, mode="intersects"),
                statuses=["work", "pre_done"],
            )
        )
        designers_target_worksheet = sheet_info.get_sheet_name("designers") or "Дизайнеры"
        designers_target_ok, designers_target_warnings = validate_render_target(
            RenderTarget(
                source_spreadsheet=source_spreadsheet,
                target_spreadsheet=target_spreadsheet,
                tasks_sheet_name=tasks_sheet_name,
                target_worksheet=str(designers_target_worksheet),
            )
        )
        if not designers_target_ok:
            return {
                "artifact": "render_v2",
                "status": "blocked",
                "mode": "render_v2",
                "render_applied": False,
                "rows_written": 0,
                "cells_written": 0,
                "target_spreadsheet": target_spreadsheet,
                "target_worksheet": designers_target_worksheet,
                "warnings": list(designers_target_warnings),
                "error": {
                    "code": "render_target_unsafe",
                    "details": {
                        "source_spreadsheet": source_spreadsheet,
                        "target_spreadsheet": target_spreadsheet,
                        "target_worksheet": designers_target_worksheet,
                        "tasks_sheet_name": tasks_sheet_name,
                    },
                },
                "duration_ms": int((perf_counter() - render_started) * 1000),
                "summary": {"task_row_issue_count": 0},
            }
        designers_usecase = DesignersRenderUseCase(
            snapshot_engine,
            timezone_name=str(APP_CONTEXT.cfg.runtime.runtime.timezone or "Europe/Moscow"),
        )
        designers_writer = GoogleSheetsPlanWriter(
            GoogleSheetsService(APP_KEY_JSON, dry_run=dry_run),
            SheetTarget(
                spreadsheet_name=sheet_info.spreadsheet_name,
                worksheet_name=designers_target_worksheet,
            ),
        )
        designers_result = RenderJob(designers_usecase, designers_writer).run(
            RenderRequest(
                window=Window(start=None, end=None, mode="intersects"),
                statuses=["work", "pre_done"],
            )
        )
        if normalized_mode == "render_v2":
            return {
                "artifact": "render_v2",
                "status": "ok",
                "mode": "render_v2",
                "force_refresh": bool(force_refresh),
                "render_applied": bool(render_result.applied or designers_result.applied),
                "rows_written": int(render_result.rows_written) + int(designers_result.rows_written),
                "cells_written": int(render_result.cells_written) + int(designers_result.cells_written),
                "target_spreadsheet": str(render_result.target_spreadsheet),
                "target_worksheet": "Задачи,Дизайнеры",
                "targets": {
                    "task_calendar": {
                        "target_worksheet": str(render_result.target_worksheet),
                        "render_applied": bool(render_result.applied),
                        "rows_written": int(render_result.rows_written),
                        "cells_written": int(render_result.cells_written),
                        "warnings": list(render_result.warnings),
                    },
                    "designers": {
                        "target_worksheet": str(designers_result.target_worksheet),
                        "render_applied": bool(designers_result.applied),
                        "rows_written": int(designers_result.rows_written),
                        "cells_written": int(designers_result.cells_written),
                        "warnings": list(designers_result.warnings),
                    },
                },
                "warnings": list(render_result.warnings) + list(designers_result.warnings),
                "duration_ms": int((perf_counter() - render_started) * 1000),
                "summary": {"task_row_issue_count": 0},
            }

    _print_quality_report(quality_report)
    return quality_report

"""Shared runtime entry for planner modes used by jobs and HTTP entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.adapters.store_ydb import build_operational_store
from src.app.bootstrap import build_app_context
from src.entrypoints.jobs.db_migrate_branch import run_db_migrate_if_requested
from src.entrypoints.jobs.db_migrate_job import run_db_migrate
from src.entrypoints.jobs.legacy_store_write_job import LegacyStoreWriteRequest, run_legacy_store_write
from src.entrypoints.jobs.quality_report_job import print_quality_report as _print_quality_report
from src.entrypoints.jobs.readmodel_freshness import (
    build_readmodel_freshness_marker as _readmodel_freshness_marker,
    safe_print as _safe_print,
)
from src.entrypoints.jobs.readmodel_probe_job import ReadmodelProbeRequest, run_readmodel_freshness_probe
from src.entrypoints.jobs.runtime_context_job import RuntimeContextRequest, resolve_runtime_context
from src.entrypoints.jobs.task_payloads import task_to_store_record as _task_to_store_record
from src.entrypoints.jobs.timer_job import TimerJob
from src.notify import ReminderFormatter, ReminderJob, ReminderRequest, ReminderUseCase, TelegramReminderSender
from src.render import GoogleSheetsPlanWriter, RenderJob, RenderRequest, RenderUseCase, SheetTarget
from src.services.sources.sheets_normalized_source import build_sheets_normalized_task_source
from src.snapshot_engine import build_snapshot_engine
from src.snapshot_engine.model import Window
from src.services.timer_pipeline import RunRequest as TimerRunRequest
from src.services.timer_pipeline import TimerPipeline
from src.services.usecases.planner_runtime import resolve_run_mode, run_planner_use_case

APP_CONTEXT = build_app_context()
APP_DEPS = APP_CONTEXT.deps
PIPELINE_CFG = APP_CONTEXT.cfg.runtime.pipeline
APP_RUNTIME_ENV = APP_CONTEXT.cfg.runtime.runtime.env_default
APP_STORE_MODE = APP_CONTEXT.cfg.runtime.sources.store_mode_default
APP_NOTIFY_SOURCE = APP_CONTEXT.cfg.runtime.sources.notify_source_default
APP_RENDER_SOURCE = APP_CONTEXT.cfg.runtime.sources.render_source_default
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
            resolve_run_mode=resolve_run_mode,
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
    store_mode = str(APP_STORE_MODE).strip().lower()
    legacy_store_mode = store_mode not in {"dual_write", "ydb_primary", "ydb_only"}
    normalized_mode = str(mode).strip().lower()
    use_legacy_planner = str(mode).startswith("legacy_planner_") or (
        legacy_store_mode and normalized_mode in {"timer", "test", "morning"}
    )
    quality_report: dict[str, Any] = {"summary": {"task_row_issue_count": 0}}

    if normalized_mode in {"reminder_v2", "reminders-only"}:
        snapshot_engine = build_snapshot_engine(APP_CONTEXT)
        usecase = ReminderUseCase(snapshot_engine)
        formatter = ReminderFormatter()
        from src.adapters.telegram import TelegramNotifier

        sender = TelegramReminderSender(
            TelegramNotifier(
                bot_token=str(APP_DEPS.get("tg_bot_token", "")),
                default_chat_id=APP_DEPS.get("default_chat_id"),
            ),
            default_chat_id=APP_DEPS.get("default_chat_id"),
        )
        await ReminderJob(usecase, formatter, sender).run(
            ReminderRequest(
                window=Window(start=None, end=None, mode="intersects"),
                statuses=["work", "pre_done"],
                group_by_owner=True,
                limit_per_owner=50,
            )
        )
        return {"artifact": "reminder_v2", "status": "ok", "summary": {"task_row_issue_count": 0}}

    if normalized_mode == "render_v2":
        snapshot_engine = build_snapshot_engine(APP_CONTEXT)
        render_usecase = RenderUseCase(snapshot_engine)
        from utils.service import GoogleSheetInfo, GoogleSheetsService

        sheet_info = GoogleSheetInfo(**APP_SHEET_INFO)
        writer = GoogleSheetsPlanWriter(
            GoogleSheetsService(APP_KEY_JSON, dry_run=dry_run),
            SheetTarget(
                spreadsheet_name=sheet_info.spreadsheet_name,
                worksheet_name=sheet_info.get_sheet_name("tasks") or "tasks",
            ),
        )
        RenderJob(render_usecase, writer).run(
            RenderRequest(
                window=Window(start=None, end=None, mode="intersects"),
                statuses=["work", "pre_done"],
            )
        )
        return {"artifact": "render_v2", "status": "ok", "summary": {"task_row_issue_count": 0}}

    if use_legacy_planner:
        from src.app.planner_bootstrap import build_planner_dependencies
        from src.entrypoints.jobs.planner_setup_job import PlannerRuntimeBuildRequest, build_planner_runtime
        from src.entrypoints.jobs.source_switch_job import apply_task_source_switches
        from src.services.planner_runtime import GoogleSheetPlanner

        planner, _ = build_planner_runtime(
            PlannerRuntimeBuildRequest(
                key_json=APP_KEY_JSON,
                sheet_info=APP_SHEET_INFO,
                dry_run=dry_run,
                mock_external=mock_external,
                cfg=APP_CONTEXT.cfg,
                mode=mode,
                render_source=APP_RENDER_SOURCE,
                notify_source=APP_NOTIFY_SOURCE,
                ydb_endpoint=APP_YDB_ENDPOINT,
                ydb_database=APP_YDB_DATABASE,
                ydb_sa_json_credentials=APP_YDB_SA_JSON_CREDENTIALS,
                ydb_sa_key_file=APP_YDB_SA_KEY_FILE,
                build_planner_dependencies=build_planner_dependencies,
                planner_cls=GoogleSheetPlanner,
                apply_task_source_switches=apply_task_source_switches,
                log=_safe_print,
            )
        )
        quality_report = await run_planner_use_case(planner, mode, allow_sync=True)

        full_snapshot = task_source.read_snapshot("A1:Z2000")
        tasks_for_legacy_store = task_source.build_tasks_from_snapshot(full_snapshot)
        if tasks_for_legacy_store:
            run_legacy_store_write(
                LegacyStoreWriteRequest(
                    legacy_blob_write=APP_LEGACY_BLOB_WRITE,
                    store_mode=APP_STORE_MODE,
                    mode=mode,
                    allow_sync=True,
                    tasks=tasks_for_legacy_store,
                    task_to_store_record=_task_to_store_record,
                    runtime_env=APP_RUNTIME_ENV,
                    ydb_endpoint=APP_YDB_ENDPOINT,
                    ydb_database=APP_YDB_DATABASE,
                    migration_store_file=APP_MIGRATION_STORE_FILE,
                    sa_json_credentials=APP_YDB_SA_JSON_CREDENTIALS,
                    sa_key_file=APP_YDB_SA_KEY_FILE,
                    build_store=build_operational_store,
                    safe_print=_safe_print,
                )
            )

    run_readmodel_freshness_probe(
        ReadmodelProbeRequest(
            mode=mode,
            render_source=APP_RENDER_SOURCE,
            notify_source=APP_NOTIFY_SOURCE,
            ydb_endpoint=APP_YDB_ENDPOINT,
            ydb_database=APP_YDB_DATABASE,
            ydb_sa_json_credentials=APP_YDB_SA_JSON_CREDENTIALS,
            ydb_sa_key_file=APP_YDB_SA_KEY_FILE,
            marker_builder=_readmodel_freshness_marker,
            safe_print=_safe_print,
        )
    )

    TimerPipeline(APP_CONTEXT).run(
        TimerRunRequest(
            mode=mode,
            force_refresh=force_refresh,
            task_source=task_source,
        )
    )
    _print_quality_report(quality_report)
    return quality_report

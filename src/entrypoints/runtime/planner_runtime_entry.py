"""Shared runtime entry for planner modes used by jobs and HTTP entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.adapters.store_ydb import build_operational_store
from src.app.bootstrap import build_app_context
from src.entrypoints.jobs.db_migrate_branch import run_db_migrate_if_requested
from src.entrypoints.jobs.db_migrate_job import run_db_migrate
from src.entrypoints.jobs.legacy_store_write_job import run_legacy_store_write
from src.entrypoints.jobs.planner_pipeline_job import (
    PlannerPipelineContext,
    PlannerPipelineRequest,
    run_planner_pipeline,
)
from src.entrypoints.jobs.quality_report_job import print_quality_report as _print_quality_report
from src.entrypoints.jobs.readmodel_freshness import (
    build_readmodel_freshness_marker as _readmodel_freshness_marker,
    safe_print as _safe_print,
)
from src.entrypoints.jobs.readmodel_probe_job import run_readmodel_freshness_probe
from src.entrypoints.jobs.readmodel_probe_job import ReadmodelProbeRequest
from src.entrypoints.jobs.runtime_context_job import RuntimeContextRequest, resolve_runtime_context
from src.entrypoints.jobs.task_payloads import (
    task_to_operational_payload as _task_to_operational_payload,
    task_to_store_record as _task_to_store_record,
)
from src.entrypoints.jobs.timer_job import TimerJob
from src.services.pipeline_runtime import (
    SyncReadmodelPipelineContext,
    SyncReadmodelPipelineRequest,
    TimerPipeline,
)
from src.services.sources.sheets_normalized_source import build_sheets_normalized_task_source
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
APP_WRITE_LEGACY_MILESTONES = bool(APP_DEPS.get("write_legacy_milestones", False))
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
    use_legacy_planner = str(mode).startswith("legacy_planner_")
    planner = None
    if use_legacy_planner:
        from src.app.planner_bootstrap import build_planner_dependencies
        from src.entrypoints.jobs.planner_setup_job import build_planner_runtime
        from src.entrypoints.jobs.source_switch_job import apply_task_source_switches
        from src.services.planner_runtime import GoogleSheetPlanner

        planner, _ = build_planner_runtime(
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
    pipeline_ctx = PlannerPipelineContext(
        task_source=task_source,
        legacy_blob_write=APP_LEGACY_BLOB_WRITE,
        app_store_mode=APP_STORE_MODE,
        app_runtime_env=APP_RUNTIME_ENV,
        migration_store_file=APP_MIGRATION_STORE_FILE,
        ydb_endpoint=APP_YDB_ENDPOINT,
        ydb_database=APP_YDB_DATABASE,
        ydb_sa_json_credentials=APP_YDB_SA_JSON_CREDENTIALS,
        ydb_sa_key_file=APP_YDB_SA_KEY_FILE,
        ydb_migrate_on_start=APP_YDB_MIGRATE_ON_START,
        write_legacy_milestones=APP_WRITE_LEGACY_MILESTONES,
        pipeline_cfg=PIPELINE_CFG,
        safe_print=_safe_print,
        run_planner_use_case=run_planner_use_case if use_legacy_planner else None,
        run_legacy_store_write=run_legacy_store_write,
        timer_pipeline_factory=lambda sync_ctx: TimerPipeline(sync_ctx),
        pipeline_sync_context_factory=SyncReadmodelPipelineContext,
        pipeline_sync_request_factory=SyncReadmodelPipelineRequest,
        task_to_store_record=_task_to_store_record,
        task_to_operational_payload=_task_to_operational_payload,
        build_store=build_operational_store,
        print_quality_report=_print_quality_report,
    )
    pipeline_request = PlannerPipelineRequest(
        planner=planner,
        use_legacy_planner=use_legacy_planner,
        mode=mode,
        force_refresh=force_refresh,
    )
    return await run_planner_pipeline(pipeline_ctx, pipeline_request)

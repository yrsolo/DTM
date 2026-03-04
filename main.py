"""Основной файл для запуска планировщика задач."""

import asyncio

from config import (
    KEY_JSON,
    LEGACY_BLOB_WRITE,
    WRITE_LEGACY_MILESTONES,
    MIGRATION_ENABLE_SOURCE_HASH_GATE,
    MIGRATION_HASH_GATE_STATE_FILE,
    MIGRATION_STORE_FILE,
    YDB_MIGRATE_ON_START,
    YDB_DATABASE,
    YDB_ENDPOINT,
    YC_SA_JSON_CREDENTIALS,
    YC_SA_KEY_FILE,
    SHEET_INFO,
)
from src.services.planner_runtime import GoogleSheetPlanner
from src.app.planner_bootstrap import build_planner_dependencies
from src.services.usecases.planner_runtime import resolve_run_mode, run_planner_use_case
from src.app.bootstrap import build_app_context
from src.adapters.store_ydb import build_operational_store
from src.entrypoints.jobs.db_migrate_branch import run_db_migrate_if_requested
from src.entrypoints.jobs.db_migrate_job import run_db_migrate
from src.entrypoints.jobs.hash_gate_job import resolve_allow_sync_by_hash_gate
from src.entrypoints.jobs.legacy_store_write_job import run_legacy_store_write
from src.entrypoints.jobs.quality_report_job import print_quality_report as _print_quality_report
from src.entrypoints.jobs.readmodel_freshness import (
    build_readmodel_freshness_marker as _readmodel_freshness_marker,
    safe_print as _safe_print,
)
from src.entrypoints.jobs.readmodel_probe_job import run_readmodel_freshness_probe
from src.entrypoints.jobs.runtime_context_job import resolve_runtime_context
from src.entrypoints.jobs.source_snapshot_reader import read_source_snapshot as _read_source_snapshot
from src.entrypoints.jobs.source_switch_job import apply_task_source_switches
from src.entrypoints.jobs.task_payloads import (
    task_to_operational_payload as _task_to_operational_payload,
    task_to_store_record as _task_to_store_record,
)
from src.entrypoints.jobs.timer_job import TimerJob
from src.services.pipeline_runtime import run_ydb_sync_readmodel_pipeline

APP_CONTEXT = build_app_context()
PIPELINE_CFG = APP_CONTEXT.cfg.runtime.pipeline
APP_RUNTIME_ENV = APP_CONTEXT.cfg.runtime.runtime.env_default
APP_STORE_MODE = APP_CONTEXT.cfg.runtime.sources.store_mode_default
APP_NOTIFY_SOURCE = APP_CONTEXT.cfg.runtime.sources.notify_source_default
APP_RENDER_SOURCE = APP_CONTEXT.cfg.runtime.sources.render_source_default
APP_TRIGGERS = APP_CONTEXT.cfg.runtime.triggers
TIMER_JOB_SHELL = TimerJob()


async def main(**kwargs):
    """Основная функция для запуска планировщика задач.

    Args:
        kwargs: Параметры запуска.
    """
    # ????????????? ????????????
    dry_run = kwargs.get("dry_run", False)
    runtime_ctx = resolve_runtime_context(
        mode=kwargs.get("mode"),
        event=kwargs.get("event"),
        dry_run=dry_run,
        mock_external=kwargs.get("mock_external"),
        force_refresh_raw=kwargs.get("force_refresh"),
        triggers=APP_TRIGGERS,
        force_refresh_default=PIPELINE_CFG.force_refresh_default,
        resolve_run_mode=resolve_run_mode,
        timer_job_shell=TIMER_JOB_SHELL,
        app_context=APP_CONTEXT,
    )
    mode = runtime_ctx.mode
    mock_external = runtime_ctx.mock_external
    force_refresh = runtime_ctx.force_refresh

    migrate_handled, migrate_result = run_db_migrate_if_requested(
        mode=mode,
        endpoint=YDB_ENDPOINT,
        database=YDB_DATABASE,
        sa_json_credentials=YC_SA_JSON_CREDENTIALS,
        sa_key_file=YC_SA_KEY_FILE,
        run_db_migrate=run_db_migrate,
    )
    if migrate_handled:
        return migrate_result

    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=dry_run,
        mock_external=mock_external,
        cfg=APP_CONTEXT.cfg,
    )
    source_task_repository = dependencies.task_repository
    planner = GoogleSheetPlanner(
        KEY_JSON,
        SHEET_INFO,
        mode=mode,
        dry_run=dry_run,
        mock_external=mock_external,
        dependencies=dependencies,
    )
    apply_task_source_switches(
        planner=planner,
        mode=mode,
        render_source=APP_RENDER_SOURCE,
        notify_source=APP_NOTIFY_SOURCE,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        ydb_sa_json_credentials=YC_SA_JSON_CREDENTIALS,
        ydb_sa_key_file=YC_SA_KEY_FILE,
        log=_safe_print,
    )
    run_readmodel_freshness_probe(
        mode=mode,
        render_source=APP_RENDER_SOURCE,
        notify_source=APP_NOTIFY_SOURCE,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        ydb_sa_json_credentials=YC_SA_JSON_CREDENTIALS,
        ydb_sa_key_file=YC_SA_KEY_FILE,
        marker_builder=_readmodel_freshness_marker,
        safe_print=_safe_print,
    )

    allow_sync = True
    allow_sync = resolve_allow_sync_by_hash_gate(
        enabled=MIGRATION_ENABLE_SOURCE_HASH_GATE,
        mode=mode,
        source_task_repository=source_task_repository,
        state_file_path=MIGRATION_HASH_GATE_STATE_FILE,
        safe_print=_safe_print,
    )

    quality_report = await run_planner_use_case(planner, mode, allow_sync=allow_sync)
    tasks = source_task_repository.get_all_tasks()

    run_legacy_store_write(
        legacy_blob_write=LEGACY_BLOB_WRITE,
        store_mode=APP_STORE_MODE,
        mode=mode,
        allow_sync=allow_sync,
        tasks=tasks,
        task_to_store_record=_task_to_store_record,
        runtime_env=APP_RUNTIME_ENV,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        migration_store_file=MIGRATION_STORE_FILE,
        sa_json_credentials=YC_SA_JSON_CREDENTIALS,
        sa_key_file=YC_SA_KEY_FILE,
        build_store=build_operational_store,
        safe_print=_safe_print,
    )

    run_ydb_sync_readmodel_pipeline(
        store_mode=APP_STORE_MODE,
        mode=mode,
        allow_sync=allow_sync,
        tasks=tasks,
        source_task_repository=source_task_repository,
        force_refresh=force_refresh,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        ydb_sa_json_credentials=YC_SA_JSON_CREDENTIALS,
        ydb_sa_key_file=YC_SA_KEY_FILE,
        ydb_migrate_on_start=YDB_MIGRATE_ON_START,
        write_legacy_milestones=WRITE_LEGACY_MILESTONES,
        runtime_env=APP_RUNTIME_ENV,
        pipeline_cfg=PIPELINE_CFG,
        safe_print=_safe_print,
        read_source_snapshot=_read_source_snapshot,
        task_to_operational_payload=_task_to_operational_payload,
    )
    _print_quality_report(quality_report)
    return quality_report


if __name__ == "__main__":
    asyncio.run(main())


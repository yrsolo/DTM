"""Planner pipeline execution helper for main job flow."""

from __future__ import annotations

from typing import Any, Awaitable, Callable


async def run_planner_pipeline(
    *,
    planner: Any,
    source_task_repository: Any,
    mode: str,
    force_refresh: bool,
    legacy_blob_write: bool,
    app_store_mode: str,
    app_runtime_env: str,
    migration_store_file: str,
    ydb_endpoint: str,
    ydb_database: str,
    ydb_sa_json_credentials: str | None,
    ydb_sa_key_file: str | None,
    ydb_migrate_on_start: bool,
    write_legacy_milestones: bool,
    pipeline_cfg: Any,
    safe_print: Callable[[str], None],
    run_planner_use_case: Callable[..., Awaitable[dict[str, Any]]],
    run_legacy_store_write: Callable[..., None],
    run_ydb_sync_readmodel_pipeline: Callable[..., None],
    task_to_store_record: Callable[[Any], dict[str, object]],
    task_to_operational_payload: Callable[[Any], dict[str, object]],
    build_store: Callable[..., Any],
    read_source_snapshot: Callable[..., dict[str, Any]],
    print_quality_report: Callable[[dict[str, Any]], None],
) -> dict[str, Any]:
    allow_sync = True

    quality_report = await run_planner_use_case(planner, mode, allow_sync=allow_sync)
    tasks = source_task_repository.get_all_tasks()

    run_legacy_store_write(
        legacy_blob_write=legacy_blob_write,
        store_mode=app_store_mode,
        mode=mode,
        allow_sync=allow_sync,
        tasks=tasks,
        task_to_store_record=task_to_store_record,
        runtime_env=app_runtime_env,
        ydb_endpoint=ydb_endpoint,
        ydb_database=ydb_database,
        migration_store_file=migration_store_file,
        sa_json_credentials=ydb_sa_json_credentials,
        sa_key_file=ydb_sa_key_file,
        build_store=build_store,
        safe_print=safe_print,
    )

    run_ydb_sync_readmodel_pipeline(
        store_mode=app_store_mode,
        mode=mode,
        allow_sync=allow_sync,
        tasks=tasks,
        source_task_repository=source_task_repository,
        force_refresh=force_refresh,
        ydb_endpoint=ydb_endpoint,
        ydb_database=ydb_database,
        ydb_sa_json_credentials=ydb_sa_json_credentials,
        ydb_sa_key_file=ydb_sa_key_file,
        ydb_migrate_on_start=ydb_migrate_on_start,
        write_legacy_milestones=write_legacy_milestones,
        runtime_env=app_runtime_env,
        pipeline_cfg=pipeline_cfg,
        safe_print=safe_print,
        read_source_snapshot=read_source_snapshot,
        task_to_operational_payload=task_to_operational_payload,
    )
    print_quality_report(quality_report)
    return quality_report

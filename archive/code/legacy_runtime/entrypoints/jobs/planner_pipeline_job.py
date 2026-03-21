"""DEPRECATED: reference-only legacy planner pipeline helper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from archive.code.legacy_runtime.entrypoints.jobs.legacy_store_write_job import LegacyStoreWriteRequest


@dataclass(frozen=True)
class PlannerPipelineContext:
    task_source: Any
    legacy_blob_write: bool
    app_store_mode: str
    app_runtime_env: str
    migration_store_file: str
    ydb_endpoint: str
    ydb_database: str
    ydb_sa_json_credentials: str | None
    ydb_sa_key_file: str | None
    ydb_migrate_on_start: bool
    write_legacy_milestones: bool
    pipeline_cfg: Any
    safe_print: Callable[[str], None]
    run_planner_use_case: Callable[..., Awaitable[dict[str, Any]]] | None
    run_legacy_store_write: Callable[[LegacyStoreWriteRequest], None]
    timer_pipeline_factory: Callable[[Any], Any]
    pipeline_sync_context_factory: Callable[..., Any]
    pipeline_sync_request_factory: Callable[..., Any]
    task_to_store_record: Callable[[Any], dict[str, object]]
    task_to_operational_payload: Callable[[Any], dict[str, object]]
    build_store: Callable[..., Any]
    print_quality_report: Callable[[dict[str, Any]], None]


@dataclass(frozen=True)
class PlannerPipelineRequest:
    planner: Any | None
    use_legacy_planner: bool
    mode: str
    force_refresh: bool


async def run_planner_pipeline(
    ctx: PlannerPipelineContext,
    request: PlannerPipelineRequest,
) -> dict[str, Any]:
    allow_sync = True

    quality_report: dict[str, Any] = {"summary": {"task_row_issue_count": 0}}
    tasks_for_legacy_store: list[Any] = []
    if request.use_legacy_planner and request.planner is not None and ctx.run_planner_use_case is not None:
        quality_report = await ctx.run_planner_use_case(request.planner, request.mode, allow_sync=allow_sync)
        full_snapshot = ctx.task_source.read_snapshot("A1:Z2000")
        tasks_for_legacy_store = ctx.task_source.build_tasks_from_snapshot(full_snapshot)

    if tasks_for_legacy_store:
        ctx.run_legacy_store_write(
            LegacyStoreWriteRequest(
                legacy_blob_write=ctx.legacy_blob_write,
                store_mode=ctx.app_store_mode,
                mode=request.mode,
                allow_sync=allow_sync,
                tasks=tasks_for_legacy_store,
                task_to_store_record=ctx.task_to_store_record,
                runtime_env=ctx.app_runtime_env,
                ydb_endpoint=ctx.ydb_endpoint,
                ydb_database=ctx.ydb_database,
                migration_store_file=ctx.migration_store_file,
                sa_json_credentials=ctx.ydb_sa_json_credentials,
                sa_key_file=ctx.ydb_sa_key_file,
                build_store=ctx.build_store,
                safe_print=ctx.safe_print,
            )
        )

    sync_ctx = ctx.pipeline_sync_context_factory(
        store_mode=ctx.app_store_mode,
        allow_sync=allow_sync,
        task_source=ctx.task_source,
        ydb_endpoint=ctx.ydb_endpoint,
        ydb_database=ctx.ydb_database,
        ydb_sa_json_credentials=ctx.ydb_sa_json_credentials,
        ydb_sa_key_file=ctx.ydb_sa_key_file,
        ydb_migrate_on_start=ctx.ydb_migrate_on_start,
        write_legacy_milestones=ctx.write_legacy_milestones,
        runtime_env=ctx.app_runtime_env,
        pipeline_cfg=ctx.pipeline_cfg,
        safe_print=ctx.safe_print,
        task_to_operational_payload=ctx.task_to_operational_payload,
    )
    sync_request = ctx.pipeline_sync_request_factory(
        mode=request.mode,
        force_refresh=request.force_refresh,
    )
    ctx.timer_pipeline_factory(sync_ctx).run(sync_request)
    ctx.print_quality_report(quality_report)
    return quality_report


"""Runtime orchestration helpers for YDB sync + readmodel pipeline."""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from src.adapters.ydb.operational_repo import OperationalTaskRepo
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.services.readmodel_builder import FrontendReadmodelBuilderService
from src.services.sync_service import YdbSyncService


@dataclass(frozen=True)
class SyncReadmodelPipelineContext:
    store_mode: str
    allow_sync: bool
    source_task_repository: Any
    ydb_endpoint: str
    ydb_database: str
    ydb_sa_json_credentials: str | None
    ydb_sa_key_file: str | None
    ydb_migrate_on_start: bool
    write_legacy_milestones: bool
    runtime_env: str
    pipeline_cfg: Any
    safe_print: Callable[[str], None]
    read_source_snapshot: Callable[..., dict[str, Any]]
    task_to_operational_payload: Callable[[Any], dict[str, Any]]


@dataclass(frozen=True)
class SyncReadmodelPipelineRequest:
    mode: str
    tasks: list[Any]
    force_refresh: bool


def run_ydb_sync_readmodel_pipeline(
    ctx: SyncReadmodelPipelineContext,
    request: SyncReadmodelPipelineRequest,
) -> None:
    """Run normalized YDB sync + readmodel build flow (feature-equivalent extract)."""

    if not (
        ctx.store_mode in {"dual_write", "ydb_primary", "ydb_only"}
        and request.mode in {"timer", "test", "sync-only"}
        and ctx.allow_sync
    ):
        return

    sync_deferred = False
    readmodel_deferred = False
    source_id = (
        "sheet:"
        f"{ctx.source_task_repository.source_sheet_info.spreadsheet_name}:"
        f"{ctx.source_task_repository.source_sheet_info.get_sheet_name('tasks')}:A1:Z2000"
    )
    ttl_skip = False
    operational_repo: OperationalTaskRepo | None = None
    try:
        operational_repo = OperationalTaskRepo(
            endpoint=ctx.ydb_endpoint,
            database=ctx.ydb_database,
            sa_json_credentials=ctx.ydb_sa_json_credentials,
            sa_key_file=ctx.ydb_sa_key_file,
            ensure_schema=ctx.ydb_migrate_on_start,
        )
        sync_service = YdbSyncService(
            operational_repo,
            write_legacy_milestones=ctx.write_legacy_milestones,
        )
        preflight_range = f"A1:Z{max(ctx.pipeline_cfg.preflight_top_rows, 1)}"
        full_range = "A1:Z2000"
        preflight_snapshot = ctx.read_source_snapshot(ctx.source_task_repository, worksheet_range=preflight_range)
        preflight_result = sync_service.run_preflight_only(
            source_id=source_id,
            preflight_range_values=preflight_snapshot,
            force_refresh=request.force_refresh,
            full_sync_interval_hours=ctx.pipeline_cfg.full_sync_interval_hours,
        )
        existing_readmodel = FrontendReadmodelRepo(
            endpoint=ctx.ydb_endpoint,
            database=ctx.ydb_database,
            sa_json_credentials=ctx.ydb_sa_json_credentials,
            sa_key_file=ctx.ydb_sa_key_file,
            ensure_schema=False,
        ).get_readmodel("frontend_v2:default")
        if existing_readmodel is not None and existing_readmodel.generated_at_utc is not None and not request.force_refresh:
            age_seconds = (datetime.now(timezone.utc) - existing_readmodel.generated_at_utc).total_seconds()
            ttl_skip = age_seconds < ctx.pipeline_cfg.readmodel_ttl_minutes * 60
        if ttl_skip:
            ctx.safe_print(
                "migration_operational_sync="
                "skipped=true "
                f"reason=readmodel_ttl_fresh ttl_minutes={ctx.pipeline_cfg.readmodel_ttl_minutes}"
            )
        else:
            if preflight_result is not None:
                ctx.safe_print("full_snapshot_fetch=skipped reason=preflight_unchanged")
                sync_result = preflight_result
            else:
                ctx.safe_print("full_snapshot_fetch=performed reason=sync_required")
                full_snapshot = ctx.read_source_snapshot(ctx.source_task_repository, worksheet_range=full_range)
                normalized_tasks = [ctx.task_to_operational_payload(task) for task in request.tasks]
                sync_result = sync_service.run(
                    source_id=source_id,
                    preflight_range_values=preflight_snapshot,
                    source_range_values=full_snapshot,
                    normalized_tasks=normalized_tasks,
                    force_refresh=request.force_refresh,
                    full_sync_interval_hours=ctx.pipeline_cfg.full_sync_interval_hours,
                )
            ctx.safe_print(
                "migration_operational_sync="
                f"source_id={sync_result.source_id} "
                f"preflight_hash_50={sync_result.preflight_hash_50} "
                f"source_hash_full={sync_result.source_hash_full} "
                f"previous_preflight_hash_50={sync_result.previous_preflight_hash_50} "
                f"previous_source_hash_full={sync_result.previous_source_hash_full} "
                f"no_changes={sync_result.no_changes} "
                f"full_sync_performed={sync_result.full_sync_performed} "
                f"forced_refresh={sync_result.forced_refresh} "
                f"tasks_upserted={sync_result.tasks_upserted} "
                f"milestones_upserted={sync_result.milestones_upserted} "
                f"ydb_queries_count={sync_result.ydb_queries_count} "
                f"error_code={sync_result.ydb_error_code}"
            )
    except Exception as exc:
        sync_deferred = True
        safe_error = str(exc).encode("ascii", "backslashreplace").decode("ascii")
        ctx.safe_print(f"migration_ydb_pipeline_error={safe_error}")
        safe_trace = traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii")
        ctx.safe_print(f"migration_ydb_pipeline_trace={safe_trace}")
        try:
            if operational_repo is not None:
                state = operational_repo.get_sync_state(source_id)
                if state is not None:
                    operational_repo.set_sync_state(
                        source_id=source_id,
                        preflight_hash_50=state.preflight_hash_50,
                        source_hash_full=state.source_hash_full,
                        synced_at_utc=datetime.now(timezone.utc),
                        last_full_sync_at_utc=state.last_full_sync_at_utc,
                        last_success_at_utc=state.last_success_at_utc or datetime.now(timezone.utc),
                        last_error=safe_error,
                        last_error_code=(
                            "ydb_resource_exhausted" if "resourceexhausted" in safe_error.lower() else "ydb_error"
                        ),
                        last_error_at_utc=datetime.now(timezone.utc),
                    )
        except Exception:
            pass
    if not sync_deferred and not ttl_skip:
        try:
            operational_repo = OperationalTaskRepo(
                endpoint=ctx.ydb_endpoint,
                database=ctx.ydb_database,
                sa_json_credentials=ctx.ydb_sa_json_credentials,
                sa_key_file=ctx.ydb_sa_key_file,
                ensure_schema=False,
            )
            readmodel_repo = FrontendReadmodelRepo(
                endpoint=ctx.ydb_endpoint,
                database=ctx.ydb_database,
                sa_json_credentials=ctx.ydb_sa_json_credentials,
                sa_key_file=ctx.ydb_sa_key_file,
                ensure_schema=False,
            )
            readmodel_builder = FrontendReadmodelBuilderService(
                operational_repo=operational_repo,
                readmodel_repo=readmodel_repo,
                source_id=source_id,
                env_name=ctx.runtime_env,
                source_sheet_name=ctx.source_task_repository.source_sheet_info.spreadsheet_name,
            )
            readmodel_result = readmodel_builder.run(
                readmodel_id="frontend_v2:default",
                force_rebuild=request.force_refresh,
            )
            ctx.safe_print(
                "migration_readmodel_build="
                f"readmodel_id={readmodel_result.readmodel_id} "
                f"source_hash={readmodel_result.source_hash} "
                f"changed={readmodel_result.changed} "
                f"tasks_count={readmodel_result.tasks_count} "
                f"ydb_queries_count={readmodel_result.ydb_queries_count}"
            )
        except Exception as exc:
            readmodel_deferred = True
            safe_error = str(exc).encode("ascii", "backslashreplace").decode("ascii")
            ctx.safe_print(f"migration_readmodel_error={safe_error}")
            safe_trace = traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii")
            ctx.safe_print(f"migration_readmodel_trace={safe_trace}")
    print(
        "migration_defer_status "
        f"sync_deferred={sync_deferred} "
        f"readmodel_deferred={readmodel_deferred}"
    )

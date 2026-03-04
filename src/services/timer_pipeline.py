"""Canonical timer pipeline runtime."""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.adapters.ydb.operational_repo import OperationalTaskRepo
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.app.context import AppContext
from src.services.mappers.task_payload_mapper import TaskPayloadMapper
from src.services.readmodel_builder import FrontendReadmodelBuilderService
from src.services.sync_service import YdbSyncService


@dataclass(frozen=True)
class RunRequest:
    mode: str
    force_refresh: bool
    task_source: Any


@dataclass(frozen=True)
class PipelineResult:
    sync_deferred: bool
    readmodel_deferred: bool
    ttl_skip: bool


class TimerPipeline:
    """Sync + readmodel pipeline using AppContext dependencies."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def run(self, request: RunRequest) -> PipelineResult:
        deps = self._ctx.deps
        cfg = self._ctx.cfg
        pipeline_cfg = cfg.runtime.pipeline
        store_mode = str(cfg.runtime.sources.store_mode_default)
        runtime_env = cfg.runtime.runtime.env_default

        if not (
            store_mode in {"dual_write", "ydb_primary", "ydb_only"}
            and request.mode in {"timer", "test", "sync-only"}
        ):
            return PipelineResult(sync_deferred=False, readmodel_deferred=False, ttl_skip=False)

        ydb_endpoint = str(deps.get("ydb_endpoint", ""))
        ydb_database = str(deps.get("ydb_database", ""))
        ydb_sa_json_credentials = deps.get("ydb_sa_json_credentials")
        ydb_sa_key_file = deps.get("ydb_sa_key_file")
        ydb_migrate_on_start = bool(deps.get("ydb_migrate_on_start", False))
        write_legacy_milestones = bool(deps.get("write_legacy_milestones", False))
        mapper = deps.get("task_payload_mapper")
        if mapper is None or not hasattr(mapper, "to_operational_payload"):
            mapper = TaskPayloadMapper()

        sync_deferred = False
        readmodel_deferred = False
        ttl_skip = False
        source_id = str(request.task_source.source_id)
        operational_repo: OperationalTaskRepo | None = None
        try:
            operational_repo = OperationalTaskRepo(
                endpoint=ydb_endpoint,
                database=ydb_database,
                sa_json_credentials=ydb_sa_json_credentials,
                sa_key_file=ydb_sa_key_file,
                ensure_schema=ydb_migrate_on_start,
            )
            sync_service = YdbSyncService(
                operational_repo,
                write_legacy_milestones=write_legacy_milestones,
            )
            preflight_range = f"A1:Z{max(pipeline_cfg.preflight_top_rows, 1)}"
            full_range = "A1:Z2000"
            preflight_snapshot = request.task_source.read_snapshot(preflight_range)
            preflight_result = sync_service.run_preflight_only(
                source_id=source_id,
                preflight_range_values=preflight_snapshot,
                force_refresh=request.force_refresh,
                full_sync_interval_hours=pipeline_cfg.full_sync_interval_hours,
            )
            existing_readmodel = FrontendReadmodelRepo(
                endpoint=ydb_endpoint,
                database=ydb_database,
                sa_json_credentials=ydb_sa_json_credentials,
                sa_key_file=ydb_sa_key_file,
                ensure_schema=False,
            ).get_readmodel("frontend_v2:default")
            if existing_readmodel is not None and existing_readmodel.generated_at_utc is not None and not request.force_refresh:
                age_seconds = (datetime.now(timezone.utc) - existing_readmodel.generated_at_utc).total_seconds()
                ttl_skip = age_seconds < pipeline_cfg.readmodel_ttl_minutes * 60
            if ttl_skip:
                self._ctx.log(
                    "migration_operational_sync="
                    "skipped=true "
                    f"reason=readmodel_ttl_fresh ttl_minutes={pipeline_cfg.readmodel_ttl_minutes}"
                )
            else:
                if preflight_result is not None:
                    self._ctx.log("full_snapshot_fetch=skipped reason=preflight_unchanged")
                    sync_result = preflight_result
                else:
                    self._ctx.log("full_snapshot_fetch=performed reason=sync_required")
                    full_snapshot = request.task_source.read_snapshot(full_range)
                    tasks = request.task_source.build_tasks_from_snapshot(full_snapshot)
                    normalized_tasks = [mapper.to_operational_payload(task) for task in tasks]
                    sync_result = sync_service.run(
                        source_id=source_id,
                        preflight_range_values=preflight_snapshot,
                        source_range_values=full_snapshot,
                        normalized_tasks=normalized_tasks,
                        force_refresh=request.force_refresh,
                        full_sync_interval_hours=pipeline_cfg.full_sync_interval_hours,
                    )
                self._ctx.log(
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
            self._ctx.log(f"migration_ydb_pipeline_error={safe_error}")
            safe_trace = traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii")
            self._ctx.log(f"migration_ydb_pipeline_trace={safe_trace}")
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
                    endpoint=ydb_endpoint,
                    database=ydb_database,
                    sa_json_credentials=ydb_sa_json_credentials,
                    sa_key_file=ydb_sa_key_file,
                    ensure_schema=False,
                )
                readmodel_repo = FrontendReadmodelRepo(
                    endpoint=ydb_endpoint,
                    database=ydb_database,
                    sa_json_credentials=ydb_sa_json_credentials,
                    sa_key_file=ydb_sa_key_file,
                    ensure_schema=False,
                )
                readmodel_builder = FrontendReadmodelBuilderService(
                    operational_repo=operational_repo,
                    readmodel_repo=readmodel_repo,
                    source_id=source_id,
                    env_name=runtime_env,
                    source_sheet_name=request.task_source.source_sheet_name,
                )
                readmodel_result = readmodel_builder.run(
                    readmodel_id="frontend_v2:default",
                    force_rebuild=request.force_refresh,
                )
                self._ctx.log(
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
                self._ctx.log(f"migration_readmodel_error={safe_error}")
                safe_trace = traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii")
                self._ctx.log(f"migration_readmodel_trace={safe_trace}")
        print(
            "migration_defer_status "
            f"sync_deferred={sync_deferred} "
            f"readmodel_deferred={readmodel_deferred}"
        )
        return PipelineResult(sync_deferred=sync_deferred, readmodel_deferred=readmodel_deferred, ttl_skip=ttl_skip)

"""Shared runtime bundle for snapshot module APIs and engine assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.platform.context import AppContext
from src.contexts.snapshot.internal.engine.prep_builder import PrepBuilder
from src.contexts.snapshot.internal.engine.query_engine import SnapshotQueryEngine
from src.contexts.snapshot.internal.engine.update_job import (
    PeopleSnapshotUpdater,
    SheetSnapshotHasher,
    SheetsTaskNormalizer,
    TaskSourceSheetsAdapter,
    UpdateJob,
)
from src.contexts.snapshot.internal.engine.stores.s3_store import build_s3_stores


@dataclass(frozen=True, slots=True)
class SnapshotRuntimeBinding:
    """Own the concrete stores and factories used by snapshot module APIs."""

    attachment_bucket: str
    raw_cache: Any
    prep_cache: Any
    extra_store: Any
    people_store: Any
    response_cache_store: Any
    query_engine: SnapshotQueryEngine
    prep_builder: PrepBuilder
    update_job_factory: Any
    people_update_job_factory: Any


def _resolve_env_prefix(value: str, env_name: str) -> str:
    token = "{env}"
    cleaned = str(value or "").strip()
    if token in cleaned:
        return cleaned.replace(token, str(env_name or "").strip().lower() or "dev")
    return cleaned


def build_snapshot_runtime_binding(ctx: AppContext) -> SnapshotRuntimeBinding:
    """Build the concrete runtime bundle consumed by snapshot APIs."""

    cfg = ctx.cfg
    deps = ctx.deps
    snap_cfg = cfg.runtime.snapshot_engine
    db_cfg = cfg.db.object_storage
    endpoint_url = str(db_cfg.get("endpoint_url_default", "")).strip()
    env_name = str(cfg.runtime.runtime.env_default).strip().lower() or "dev"
    raw_cache, prep_cache, extra_store, people_store, response_cache_store = build_s3_stores(
        bucket=str(snap_cfg.bucket).strip(),
        endpoint_url=endpoint_url,
        aws_access_key_id=deps.get("aws_access_key_id"),
        aws_secret_access_key=deps.get("aws_secret_access_key"),
        raw_key=_resolve_env_prefix(str(snap_cfg.prefix_raw), env_name),
        prep_key=_resolve_env_prefix(str(snap_cfg.prefix_prep), env_name),
        extra_prefix=_resolve_env_prefix(str(snap_cfg.prefix_extra), env_name),
        people_key=_resolve_env_prefix(str(snap_cfg.prefix_people), env_name),
        response_prefix=_resolve_env_prefix(str(snap_cfg.prefix_responses), env_name),
    )
    prep_builder = PrepBuilder(extra_store)
    query_engine = SnapshotQueryEngine(
        env_name=cfg.runtime.runtime.env_default,
        source_sheet_name=str(cfg.tables.google_sheets.get("source_sheet_name_default", "")),
    )

    def _update_job_factory(task_source: Any) -> UpdateJob:
        return UpdateJob(
            source=TaskSourceSheetsAdapter(task_source),
            hasher=SheetSnapshotHasher(),
            normalizer=SheetsTaskNormalizer(),
            raw_cache=raw_cache,
            prep_cache=prep_cache,
            prep_builder=prep_builder,
        )

    def _people_update_job_factory(_task_source: Any) -> PeopleSnapshotUpdater:
        people_field_map = dict(cfg.tables.field_maps.get("people", {}))
        return PeopleSnapshotUpdater(
            people_store=people_store,
            source_id=f"sheet:{cfg.tables.google_sheets.get('source_sheet_name_default', '')}:people:A1:Z200",
            people_field_map=people_field_map,
        )

    return SnapshotRuntimeBinding(
        attachment_bucket=str(snap_cfg.bucket).strip(),
        raw_cache=raw_cache,
        prep_cache=prep_cache,
        extra_store=extra_store,
        people_store=people_store,
        response_cache_store=response_cache_store,
        query_engine=query_engine,
        prep_builder=prep_builder,
        update_job_factory=_update_job_factory,
        people_update_job_factory=_people_update_job_factory,
    )

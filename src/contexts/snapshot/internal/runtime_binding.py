"""Role-true runtime builders for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.contexts.snapshot.internal.attachment_mutations import SnapshotAttachmentMutationService
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
from src.platform.context import AppContext


@dataclass(frozen=True, slots=True)
class SnapshotStores:
    """Store bundle shared across snapshot application services."""

    attachment_bucket: str
    raw_cache: Any
    prep_cache: Any
    extra_store: Any
    people_store: Any
    response_cache_store: Any


def _resolve_env_prefix(value: str, env_name: str) -> str:
    token = "{env}"
    cleaned = str(value or "").strip()
    if token in cleaned:
        return cleaned.replace(token, str(env_name or "").strip().lower() or "dev")
    return cleaned


def build_snapshot_stores(ctx: AppContext) -> SnapshotStores:
    """Build the concrete store bundle shared by snapshot APIs."""

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
    return SnapshotStores(
        attachment_bucket=str(snap_cfg.bucket).strip(),
        raw_cache=raw_cache,
        prep_cache=prep_cache,
        extra_store=extra_store,
        people_store=people_store,
        response_cache_store=response_cache_store,
    )


def build_snapshot_prep_builder(stores: SnapshotStores) -> PrepBuilder:
    """Build the prep builder over the shared snapshot extra store."""

    return PrepBuilder(stores.extra_store)


def build_snapshot_query_engine(ctx: AppContext) -> SnapshotQueryEngine:
    """Build the frontend query engine for snapshot reads."""

    return SnapshotQueryEngine(
        env_name=ctx.cfg.runtime.runtime.env_default,
        source_sheet_name=str(ctx.cfg.tables.google_sheets.get("source_sheet_name_default", "")),
    )


def build_snapshot_attachment_mutation_service(
    ctx: AppContext,
    *,
    stores: SnapshotStores | None = None,
) -> SnapshotAttachmentMutationService:
    """Build the attachment mutation service for snapshot projection updates."""

    active_stores = stores or build_snapshot_stores(ctx)
    return SnapshotAttachmentMutationService(
        attachment_bucket=active_stores.attachment_bucket,
        raw_cache=active_stores.raw_cache,
        prep_cache=active_stores.prep_cache,
        extra_store=active_stores.extra_store,
        prep_builder=build_snapshot_prep_builder(active_stores),
    )


def run_snapshot_update(ctx: AppContext, *, task_source: Any, force: bool = False):
    """Run the snapshot update flow without exposing a broad runtime bag."""

    stores = build_snapshot_stores(ctx)
    prep_builder = build_snapshot_prep_builder(stores)
    update_job = UpdateJob(
        source=TaskSourceSheetsAdapter(task_source),
        hasher=SheetSnapshotHasher(),
        normalizer=SheetsTaskNormalizer(),
        raw_cache=stores.raw_cache,
        prep_cache=stores.prep_cache,
        prep_builder=prep_builder,
    )
    result = update_job.run(force=force)
    people_field_map = dict(ctx.cfg.tables.field_maps.get("people", {}))
    people_updater = PeopleSnapshotUpdater(
        people_store=stores.people_store,
        source_id=f"sheet:{ctx.cfg.tables.google_sheets.get('source_sheet_name_default', '')}:people:A1:Z200",
        people_field_map=people_field_map,
    )
    people_updater.run(TaskSourceSheetsAdapter(task_source))
    return result


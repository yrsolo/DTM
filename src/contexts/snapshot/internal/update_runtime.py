"""Update-runner builders for the snapshot context."""

from __future__ import annotations

from typing import Any

from src.contexts.snapshot.internal.engine.update_job import (
    PeopleSnapshotUpdater,
    SheetSnapshotHasher,
    SheetsTaskNormalizer,
    TaskSourceSheetsAdapter,
    UpdateJob,
)
from src.platform.context import AppContext

from .query_runtime import build_snapshot_prep_builder
from .stores import build_snapshot_stores


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

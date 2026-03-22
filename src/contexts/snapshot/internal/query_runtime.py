"""Query-side builders for the snapshot context."""

from __future__ import annotations

from src.contexts.snapshot.internal.engine.prep_builder import PrepBuilder
from src.contexts.snapshot.internal.engine.query_engine import SnapshotQueryEngine
from src.platform.context import AppContext

from .stores import SnapshotStores


def build_snapshot_prep_builder(stores: SnapshotStores) -> PrepBuilder:
    """Build the prep builder over the shared snapshot extra store."""

    return PrepBuilder(stores.extra_store)


def build_snapshot_query_engine(ctx: AppContext) -> SnapshotQueryEngine:
    """Build the frontend query engine for snapshot reads."""

    return SnapshotQueryEngine(
        env_name=ctx.cfg.runtime.runtime.env_default,
        source_sheet_name=str(ctx.cfg.tables.google_sheets.get("source_sheet_name_default", "")),
    )

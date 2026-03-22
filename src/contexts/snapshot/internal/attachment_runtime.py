"""Attachment-mutation builders for the snapshot context."""

from __future__ import annotations

from src.contexts.snapshot.internal.attachment_mutations import SnapshotAttachmentMutationService
from src.platform.context import AppContext

from .query_runtime import build_snapshot_prep_builder
from .stores import SnapshotStores, build_snapshot_stores


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

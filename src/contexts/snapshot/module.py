"""Module surface for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from .application.capabilities import (
    SnapshotAttachmentApi,
    SnapshotQueryApi,
    SnapshotReadApi,
    SnapshotUpdateApi,
)
from .internal.attachment_runtime import (
    build_snapshot_attachment_mutation_service,
)
from .internal.query_runtime import (
    build_snapshot_query_engine,
)
from .internal.stores import (
    build_snapshot_stores,
)
from .internal.update_runtime import (
    run_snapshot_update,
)


@dataclass(frozen=True, slots=True)
class SnapshotModule:
    """Own the snapshot read-model surface and exported application APIs."""

    name: str = "snapshot"

    def read_api(self, ctx) -> SnapshotReadApi:
        stores = build_snapshot_stores(ctx)
        return SnapshotReadApi(
            _prep_snapshot_getter=stores.prep_cache.get,
            _people_snapshot_getter=stores.people_store.get,
        )

    def attachment_api(self, ctx) -> SnapshotAttachmentApi:
        stores = build_snapshot_stores(ctx)
        return SnapshotAttachmentApi(
            _prep_snapshot_getter=stores.prep_cache.get,
            _response_cache_store=stores.response_cache_store,
            _mutation_service_builder=lambda: build_snapshot_attachment_mutation_service(ctx, stores=stores),
        )

    def query_api(self, ctx) -> SnapshotQueryApi:
        stores = build_snapshot_stores(ctx)
        query_engine = build_snapshot_query_engine(ctx)
        return SnapshotQueryApi(
            _prep_snapshot_getter=stores.prep_cache.get,
            _raw_snapshot_getter=stores.raw_cache.get,
            _people_snapshot_getter=stores.people_store.get,
            _response_cache_store=stores.response_cache_store,
            _frontend_query_executor=lambda prep, query: query_engine.query_frontend_v2(
                prep,
                query,
            ),
        )

    def update_api(self, ctx) -> SnapshotUpdateApi:
        return SnapshotUpdateApi(
            _update_runner=lambda *, task_source, force=False: run_snapshot_update(
                ctx,
                task_source=task_source,
                force=force,
            )
        )


def get_module() -> SnapshotModule:
    """Return the canonical module surface for the snapshot context."""

    return SnapshotModule()


def get_read_api(ctx) -> SnapshotReadApi:
    return get_module().read_api(ctx)


def get_attachment_api(ctx) -> SnapshotAttachmentApi:
    return get_module().attachment_api(ctx)


def get_query_api(ctx) -> SnapshotQueryApi:
    return get_module().query_api(ctx)


def get_update_api(ctx) -> SnapshotUpdateApi:
    return get_module().update_api(ctx)

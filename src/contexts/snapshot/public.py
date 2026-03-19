"""Public facade for the snapshot context."""

from __future__ import annotations

from .contracts import Window
from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_snapshot_engine(ctx):
    return get_module().build_engine(ctx)


def get_prep_snapshot(ctx):
    return get_module().get_prep_snapshot(ctx)


def get_raw_snapshot(ctx):
    return get_module().get_raw_snapshot(ctx)


def get_people_snapshot(ctx):
    return get_module().get_people_snapshot(ctx)


def get_response_cache_store(ctx):
    return get_module().get_response_cache_store(ctx)


def query_frontend_v2(ctx, query):
    return get_module().query_frontend_v2(ctx, query)


def get_update_snapshot_job(ctx):
    """Return the owning snapshot update job runner."""

    from src.jobs.update_snapshot_job import UpdateSnapshotJob

    return UpdateSnapshotJob(ctx)


__all__ = [
    "Window",
    "get_people_snapshot",
    "get_prep_snapshot",
    "get_public_api",
    "get_raw_snapshot",
    "get_response_cache_store",
    "get_snapshot_engine",
    "get_update_snapshot_job",
    "query_frontend_v2",
]

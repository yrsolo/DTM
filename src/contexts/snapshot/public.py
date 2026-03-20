"""Public facade for the snapshot context."""

from __future__ import annotations

from src.commands.types import UPDATE_SNAPSHOT

from .contracts import Window
from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_snapshot_engine(ctx):
    return get_module().build_engine(ctx)


def get_read_capability(ctx):
    return get_module().build_read_capability(ctx)


def get_attachment_capability(ctx):
    return get_module().build_attachment_capability(ctx)


def get_query_capability(ctx):
    return get_module().build_query_capability(ctx)


def get_update_capability(ctx):
    return get_module().build_update_capability(ctx)


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

    from .application import UpdateSnapshotJob

    return UpdateSnapshotJob(ctx)


def get_command_handlers(ctx) -> dict[str, object]:
    """Return the snapshot-owned queue command handlers."""

    return {UPDATE_SNAPSHOT: get_update_snapshot_job(ctx)}


__all__ = [
    "Window",
    "get_attachment_capability",
    "get_people_snapshot",
    "get_prep_snapshot",
    "get_public_api",
    "get_query_capability",
    "get_raw_snapshot",
    "get_read_capability",
    "get_response_cache_store",
    "get_snapshot_engine",
    "get_update_capability",
    "get_update_snapshot_job",
    "query_frontend_v2",
]

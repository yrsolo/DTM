"""Public facade for the snapshot context."""

from __future__ import annotations

from src.commands.types import UPDATE_SNAPSHOT

from .contracts import Window
from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_read_capability(ctx):
    return get_module().read_capability(ctx)


def get_attachment_capability(ctx):
    return get_module().attachment_capability(ctx)


def get_query_capability(ctx):
    return get_module().query_capability(ctx)


def get_update_capability(ctx):
    return get_module().update_capability(ctx)

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
    "get_public_api",
    "get_query_capability",
    "get_read_capability",
    "get_update_capability",
    "get_update_snapshot_job",
]

"""Public facade for the snapshot context."""

from __future__ import annotations

from src.platform.runtime.commands.types import UPDATE_SNAPSHOT

from .contracts import Window
from .module import get_attachment_api, get_module, get_query_api, get_read_api, get_update_api


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_read_capability(ctx):
    return get_read_api(ctx)


def get_attachment_capability(ctx):
    return get_attachment_api(ctx)


def get_query_capability(ctx):
    return get_query_api(ctx)


def get_update_capability(ctx):
    return get_update_api(ctx)

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


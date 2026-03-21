"""Module surface for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from .application.capabilities import (
    SnapshotAttachmentApi,
    SnapshotQueryApi,
    SnapshotReadApi,
    SnapshotUpdateApi,
)


@dataclass(frozen=True, slots=True)
class SnapshotModule:
    """Own the snapshot read-model surface and exported application APIs."""

    name: str = "snapshot"

    def read_api(self, ctx) -> SnapshotReadApi:
        return SnapshotReadApi(ctx)

    def attachment_api(self, ctx) -> SnapshotAttachmentApi:
        return SnapshotAttachmentApi(ctx)

    def query_api(self, ctx) -> SnapshotQueryApi:
        return SnapshotQueryApi(ctx)

    def update_api(self, ctx) -> SnapshotUpdateApi:
        return SnapshotUpdateApi(ctx)


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

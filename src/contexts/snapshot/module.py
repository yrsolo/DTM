"""Module surface for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from .application.capabilities import (
    SnapshotAttachmentCapability,
    SnapshotQueryCapability,
    SnapshotReadCapability,
    SnapshotUpdateCapability,
)


@dataclass(frozen=True, slots=True)
class SnapshotModule:
    """Own the snapshot read-model surface and exported capabilities."""

    name: str = "snapshot"

    def read_capability(self, ctx) -> SnapshotReadCapability:
        return SnapshotReadCapability(ctx)

    def attachment_capability(self, ctx) -> SnapshotAttachmentCapability:
        return SnapshotAttachmentCapability(ctx)

    def query_capability(self, ctx) -> SnapshotQueryCapability:
        return SnapshotQueryCapability(ctx)

    def update_capability(self, ctx) -> SnapshotUpdateCapability:
        return SnapshotUpdateCapability(ctx)


def get_module() -> SnapshotModule:
    """Return the canonical module surface for the snapshot context."""

    return SnapshotModule()

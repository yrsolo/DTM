"""Local builder for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass

from src.snapshot_engine import build_snapshot_engine


@dataclass(frozen=True, slots=True)
class SnapshotModule:
    """Context-local builder bundle used during staged migration."""

    name: str = "snapshot"

    def build_engine(self, ctx):
        return build_snapshot_engine(ctx)


def get_module() -> SnapshotModule:
    """Return the local module instance for the snapshot context."""

    return SnapshotModule()

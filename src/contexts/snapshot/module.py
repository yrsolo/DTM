"""Local builder placeholder for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SnapshotModule:
    """Context-local module placeholder used during staged migration."""

    name: str = "snapshot"


def get_module() -> SnapshotModule:
    """Return a minimal local module instance until real wiring moves here."""

    return SnapshotModule()


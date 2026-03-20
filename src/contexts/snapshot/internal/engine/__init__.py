"""Snapshot engine public exports with lazy loading to avoid import cycles."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.contexts.snapshot.internal.engine.engine import SnapshotEngine, SnapshotFrontendQuery


def build_snapshot_engine(*args, **kwargs):
    from src.contexts.snapshot.internal.engine.engine import build_snapshot_engine as _build_snapshot_engine

    return _build_snapshot_engine(*args, **kwargs)


def __getattr__(name: str):
    if name in {"SnapshotEngine", "SnapshotFrontendQuery", "build_snapshot_engine"}:
        from src.contexts.snapshot.internal.engine import engine as _engine

        return getattr(_engine, name)
    raise AttributeError(name)


__all__ = ["SnapshotEngine", "SnapshotFrontendQuery", "build_snapshot_engine"]

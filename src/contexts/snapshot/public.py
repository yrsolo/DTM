"""Public facade for the snapshot context."""

from __future__ import annotations

from .contracts import Window
from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_snapshot_engine(ctx):
    return get_module().build_engine(ctx)


__all__ = ["Window", "get_public_api", "get_snapshot_engine"]

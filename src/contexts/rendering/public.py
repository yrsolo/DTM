"""Public facade for the rendering context."""

from __future__ import annotations

from .module import get_module


def get_execution_api(ctx):
    """Return the canonical rendering execution surface."""

    return get_module().execution_api(ctx)


def get_command_handlers(ctx) -> dict[str, object]:
    """Return the rendering-owned queue command handlers."""

    return get_module().command_handlers(ctx)


__all__ = ["get_command_handlers", "get_execution_api"]


"""Public reminder delivery entry for the reminders context."""

from __future__ import annotations

from .module import get_module


def get_delivery_api(ctx):
    """Return the canonical reminder delivery surface."""

    return get_module().delivery_api(ctx)


def get_command_handlers(ctx) -> dict[str, object]:
    """Return the reminders-owned queue command handlers."""

    return get_module().command_handlers(ctx)


__all__ = ["get_command_handlers", "get_delivery_api"]

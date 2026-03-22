"""Public facade for the telegram interaction context."""

from __future__ import annotations

from src.platform.runtime.commands.types import GROUP_QUERY_REPLY

from .module import get_module


def get_interaction_api(ctx):
    """Return the canonical telegram interaction surface."""

    return get_module().interaction_api(ctx)


def get_webhook_handler(ctx):
    return get_interaction_api(ctx).webhook_handler()

def get_command_handlers(ctx) -> dict[str, object]:
    """Return the telegram-owned queue command handlers."""

    from .internal.job_runner import GroupQueryReplyJob

    return {GROUP_QUERY_REPLY: GroupQueryReplyJob(ctx)}


__all__ = ["get_command_handlers", "get_interaction_api", "get_webhook_handler"]


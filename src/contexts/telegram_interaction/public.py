"""Public facade for the telegram interaction context."""

from __future__ import annotations

from src.commands.types import GROUP_QUERY_REPLY

from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_update_parser():
    return get_module().build_update_parser()


def get_command_router():
    return get_module().build_command_router()


def get_webhook_handler(ctx):
    return get_module().build_webhook_handler(ctx)


def get_snapshot_read_capability(ctx):
    return get_module().build_snapshot_read_capability(ctx)


def get_usecase(snapshot_read):
    return get_module().build_usecase(snapshot_read)


def get_group_query_formatter():
    return get_module().build_group_query_formatter()


def get_sender(ctx):
    return get_module().build_sender(ctx)


def build_group_query_request(**kwargs):
    return get_module().build_request(**kwargs)


def get_group_query_reply_job(ctx):
    """Return the owning Telegram interaction job runner for group-query replies."""

    from .internal.job_runner import GroupQueryReplyJob

    return GroupQueryReplyJob(ctx)


def get_command_handlers(ctx) -> dict[str, object]:
    """Return the telegram-owned queue command handlers."""

    return {GROUP_QUERY_REPLY: get_group_query_reply_job(ctx)}

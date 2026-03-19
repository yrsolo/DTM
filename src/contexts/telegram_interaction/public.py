"""Public facade for the telegram interaction context."""

from __future__ import annotations

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


def get_snapshot_engine(ctx):
    return get_module().build_snapshot_engine(ctx)


def get_usecase(snapshot_engine):
    return get_module().build_usecase(snapshot_engine)


def get_group_query_formatter():
    return get_module().build_group_query_formatter()


def get_sender(ctx):
    return get_module().build_sender(ctx)

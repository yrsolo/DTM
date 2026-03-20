"""Public facade for the access API context."""

from __future__ import annotations

from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_browser_routes_handler(ctx):
    return get_module().build_browser_routes_handler(ctx)


def get_frontend_root_handler(ctx):
    return get_module().build_frontend_root_handler(ctx)


def get_frontend_v2_handler(ctx):
    return get_module().build_frontend_v2_handler(ctx)


def get_info_handler(ctx):
    return get_module().build_info_handler(ctx)


def get_people_snapshot_handler(ctx):
    return get_module().build_people_snapshot_handler(ctx)


def get_task_attachment_read_handler(ctx):
    return get_module().build_task_attachment_read_handler(ctx)

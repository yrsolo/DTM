"""Public facade for the rendering context."""

from __future__ import annotations

from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_snapshot_read_capability(ctx):
    return get_module().build_snapshot_read_capability(ctx)


def get_timeline_usecase(snapshot_read, *, timezone_name: str):
    return get_module().build_timeline_usecase(snapshot_read, timezone_name=timezone_name)


def get_designers_usecase(snapshot_read, *, timezone_name: str):
    return get_module().build_designers_usecase(snapshot_read, timezone_name=timezone_name)


def get_window(*, start=None, end=None, mode: str = "intersects"):
    return get_module().build_window(start=start, end=end, mode=mode)


def get_request(*, window, statuses):
    return get_module().build_request(window=window, statuses=statuses)


def get_writer(service, *, spreadsheet_name, worksheet_name):
    return get_module().build_writer(service, spreadsheet_name=spreadsheet_name, worksheet_name=worksheet_name)


def get_render_job(usecase, writer):
    return get_module().build_job(usecase, writer)


def get_render_timeline_job(ctx):
    """Return the owning rendering job runner for timeline sheets."""

    from src.jobs.render_timeline_job import RenderTimelineJob

    return RenderTimelineJob(ctx)


def get_render_designers_job(ctx):
    """Return the owning rendering job runner for designers sheets."""

    from src.jobs.render_designers_job import RenderDesignersJob

    return RenderDesignersJob(ctx)

"""Public facade for the rendering context."""

from __future__ import annotations

from src.platform.runtime.commands.types import RENDER_DESIGNERS_SHEET, RENDER_TIMELINE_SHEET

from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_snapshot_read_api(ctx):
    return get_module().snapshot_read_api(ctx)


def get_timeline_usecase(snapshot_read, *, timezone_name: str):
    return get_module().timeline_usecase(snapshot_read, timezone_name=timezone_name)


def get_designers_usecase(snapshot_read, *, timezone_name: str):
    return get_module().designers_usecase(snapshot_read, timezone_name=timezone_name)


def get_window(*, start=None, end=None, mode: str = "intersects"):
    return get_module().window(start=start, end=end, mode=mode)


def get_request(*, window, statuses):
    return get_module().request(window=window, statuses=statuses)


def get_writer(service, *, spreadsheet_name, worksheet_name):
    return get_module().writer(service, spreadsheet_name=spreadsheet_name, worksheet_name=worksheet_name)


def get_render_job(usecase, writer):
    return get_module().job(usecase, writer)


def get_render_timeline_job(ctx):
    """Return the owning rendering job runner for timeline sheets."""

    from .internal.job_runners import RenderTimelineJob

    return RenderTimelineJob(ctx)


def get_render_designers_job(ctx):
    """Return the owning rendering job runner for designers sheets."""

    from .internal.job_runners import RenderDesignersJob

    return RenderDesignersJob(ctx)


def get_command_handlers(ctx) -> dict[str, object]:
    """Return the rendering-owned queue command handlers."""

    return {
        RENDER_TIMELINE_SHEET: get_render_timeline_job(ctx),
        RENDER_DESIGNERS_SHEET: get_render_designers_job(ctx),
    }


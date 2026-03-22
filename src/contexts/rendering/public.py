"""Public facade for the rendering context."""

from __future__ import annotations

from src.platform.runtime.commands.types import RENDER_DESIGNERS_SHEET, RENDER_TIMELINE_SHEET

from .module import get_module


def get_execution_api(ctx):
    """Return the canonical rendering execution surface."""

    return get_module().execution_api(ctx)


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


__all__ = ["get_command_handlers", "get_execution_api"]


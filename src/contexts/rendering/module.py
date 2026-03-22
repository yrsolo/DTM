"""Module surface for the rendering context."""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.snapshot.contracts import Window
from src.contexts.snapshot.module import get_read_api
from src.platform.runtime.commands.types import RENDER_DESIGNERS_SHEET, RENDER_TIMELINE_SHEET

from .application.execution_api import RenderingExecutionApi
from .internal import DesignersRenderUseCase, GoogleSheetsPlanWriter, RenderJob, RenderRequest, RenderUseCase, SheetTarget


@dataclass(frozen=True, slots=True)
class RenderingModule:
    """Own the rendering use-cases built on top of snapshot read contracts."""

    name: str = "rendering"

    def snapshot_read_api(self, ctx):
        return get_read_api(ctx)

    def timeline_usecase(self, snapshot_read, *, timezone_name: str):
        return RenderUseCase(snapshot_read, timezone_name=timezone_name)

    def designers_usecase(self, snapshot_read, *, timezone_name: str):
        return DesignersRenderUseCase(snapshot_read, timezone_name=timezone_name)

    def window(self, *, start=None, end=None, mode: str = "intersects"):
        return Window(start=start, end=end, mode=mode)

    def request(self, *, window, statuses):
        return RenderRequest(window=window, statuses=list(statuses))

    def sheet_target(self, *, spreadsheet_name, worksheet_name):
        return SheetTarget(spreadsheet_name=spreadsheet_name, worksheet_name=worksheet_name)

    def writer(self, service, *, spreadsheet_name, worksheet_name):
        return GoogleSheetsPlanWriter(
            service,
            self.sheet_target(spreadsheet_name=spreadsheet_name, worksheet_name=worksheet_name),
        )

    def job(self, usecase, writer):
        return RenderJob(usecase, writer)

    def execution_api(self, ctx):
        return RenderingExecutionApi(ctx, self)

    def command_handlers(self, ctx) -> dict[str, object]:
        from .internal.job_runners import RenderDesignersJob, RenderTimelineJob

        return {
            RENDER_TIMELINE_SHEET: RenderTimelineJob(ctx),
            RENDER_DESIGNERS_SHEET: RenderDesignersJob(ctx),
        }


def get_module() -> RenderingModule:
    """Return the canonical module surface for the rendering context."""

    return RenderingModule()

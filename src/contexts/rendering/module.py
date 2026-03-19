"""Local builder for the rendering context."""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.snapshot.contracts import Window
from src.contexts.snapshot.public import get_snapshot_engine
from src.render import DesignersRenderUseCase, GoogleSheetsPlanWriter, RenderJob, RenderRequest, RenderUseCase, SheetTarget


@dataclass(frozen=True, slots=True)
class RenderingModule:
    """Context-local builder bundle used during staged migration."""

    name: str = "rendering"

    def build_snapshot_engine(self, ctx):
        return get_snapshot_engine(ctx)

    def build_timeline_usecase(self, snapshot_engine, *, timezone_name: str):
        return RenderUseCase(snapshot_engine, timezone_name=timezone_name)

    def build_designers_usecase(self, snapshot_engine, *, timezone_name: str):
        return DesignersRenderUseCase(snapshot_engine, timezone_name=timezone_name)

    def build_window(self, *, start=None, end=None, mode: str = "intersects"):
        return Window(start=start, end=end, mode=mode)

    def build_request(self, *, window, statuses):
        return RenderRequest(window=window, statuses=list(statuses))

    def build_sheet_target(self, *, spreadsheet_name, worksheet_name):
        return SheetTarget(spreadsheet_name=spreadsheet_name, worksheet_name=worksheet_name)

    def build_writer(self, service, *, spreadsheet_name, worksheet_name):
        return GoogleSheetsPlanWriter(
            service,
            self.build_sheet_target(spreadsheet_name=spreadsheet_name, worksheet_name=worksheet_name),
        )

    def build_job(self, usecase, writer):
        return RenderJob(usecase, writer)


def get_module() -> RenderingModule:
    """Return the local module instance for the rendering context."""

    return RenderingModule()

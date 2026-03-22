"""Application-owned rendering execution surface."""

from __future__ import annotations

from src.platform.context import AppContext


class RenderingExecutionApi:
    """Own rendering job assembly for timeline and designers outputs."""

    def __init__(self, ctx: AppContext, module) -> None:  # noqa: ANN001
        self._ctx = ctx
        self._module = module

    def snapshot_read_api(self):
        return self._module.snapshot_read_api(self._ctx)

    def timeline_usecase(self, snapshot_read=None, *, timezone_name: str):  # noqa: ANN001
        if snapshot_read is None:
            snapshot_read = self.snapshot_read_api()
        return self._module.timeline_usecase(snapshot_read, timezone_name=timezone_name)

    def designers_usecase(self, snapshot_read=None, *, timezone_name: str):  # noqa: ANN001
        if snapshot_read is None:
            snapshot_read = self.snapshot_read_api()
        return self._module.designers_usecase(snapshot_read, timezone_name=timezone_name)

    def window(self, *, start=None, end=None, mode: str = "intersects"):
        return self._module.window(start=start, end=end, mode=mode)

    def request(self, *, window, statuses):
        return self._module.request(window=window, statuses=statuses)

    def writer(self, service, *, spreadsheet_name, worksheet_name):
        return self._module.writer(
            service,
            spreadsheet_name=spreadsheet_name,
            worksheet_name=worksheet_name,
        )

    def job(self, usecase, writer):
        return self._module.job(usecase, writer)


__all__ = ["RenderingExecutionApi"]

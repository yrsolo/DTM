from __future__ import annotations

from dataclasses import replace
from time import perf_counter

from .model import RenderApplyResult, RenderRequest
from .sheets_adapter import SheetsWriter
from .usecase import RenderUseCase


class RenderJob:
    def __init__(self, usecase: RenderUseCase, writer: SheetsWriter):
        self._usecase = usecase
        self._writer = writer

    def run(self, req: RenderRequest) -> RenderApplyResult:
        started_at = perf_counter()
        build_started = perf_counter()
        plan = self._usecase.build_plan(req)
        build_plan_ms = (perf_counter() - build_started) * 1000.0
        write_started = perf_counter()
        result = self._writer.apply(plan)
        write_sheet_ms = (perf_counter() - write_started) * 1000.0
        return replace(
            result,
            build_plan_ms=build_plan_ms,
            write_sheet_ms=write_sheet_ms,
            total_duration_ms=(perf_counter() - started_at) * 1000.0,
        )

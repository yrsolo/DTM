from __future__ import annotations

from .model import RenderApplyResult
from .model import RenderRequest
from .sheets_adapter import SheetsWriter
from .usecase import RenderUseCase


class RenderJob:
    def __init__(self, usecase: RenderUseCase, writer: SheetsWriter):
        self._usecase = usecase
        self._writer = writer

    def run(self, req: RenderRequest) -> RenderApplyResult:
        plan = self._usecase.build_plan(req)
        return self._writer.apply(plan)

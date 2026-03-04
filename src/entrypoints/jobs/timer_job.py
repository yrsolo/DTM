"""Thin timer job orchestration scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.app.context import AppContext
from src.services.usecases.contracts import (
    BuildReadmodelUseCase,
    NotifyUseCase,
    RenderUseCase,
    SyncUseCase,
)


@dataclass(slots=True)
class TimerJob:
    """Linear orchestration shell for timer pipeline."""

    sync: SyncUseCase | None = None
    build_readmodel: BuildReadmodelUseCase | None = None
    render: RenderUseCase | None = None
    notify: NotifyUseCase | None = None

    def run(self, ctx: AppContext) -> dict[str, Any]:
        """Execute connected steps in fixed order.

        Current phase intentionally does not alter existing runtime flow.
        Job can be adopted by `main.py` in follow-up tasks.
        """

        report: dict[str, Any] = {"steps": []}
        if self.sync is not None:
            sync_result = self.sync.run(ctx)
            report["steps"].append({"step": "sync", "success": bool(sync_result.success)})
            if not sync_result.success:
                return report
        if self.build_readmodel is not None:
            build_result = self.build_readmodel.run(ctx)
            report["steps"].append({"step": "build_readmodel", "success": bool(build_result.success)})
            if not build_result.success:
                return report
        if self.render is not None:
            render_result = self.render.run(ctx)
            report["steps"].append({"step": "render", "success": bool(render_result.success)})
        if self.notify is not None:
            notify_result = self.notify.run(ctx)
            report["steps"].append({"step": "notify", "success": bool(notify_result.success)})
        return report


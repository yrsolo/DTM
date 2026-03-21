"""Thin timer job orchestration scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.app.context import AppContext


@dataclass(slots=True)
class SyncResult:
    success: bool
    changed: bool
    message: str = ""


@dataclass(slots=True)
class BuildResult:
    success: bool
    built: bool
    message: str = ""


@dataclass(slots=True)
class RenderResult:
    success: bool
    rendered: bool
    message: str = ""


@dataclass(slots=True)
class NotifyResult:
    success: bool
    sent: bool
    message: str = ""


class SyncUseCase(Protocol):
    def run(self, ctx: AppContext) -> SyncResult: ...


class BuildReadmodelUseCase(Protocol):
    def run(self, ctx: AppContext) -> BuildResult: ...


class RenderUseCase(Protocol):
    def run(self, ctx: AppContext) -> RenderResult: ...


class NotifyUseCase(Protocol):
    def run(self, ctx: AppContext) -> NotifyResult: ...


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

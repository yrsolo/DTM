"""Shared use-case result contracts for clean pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.app.context import AppContext


@dataclass(slots=True)
class SyncResult:
    """Outcome contract for sync use-case."""

    success: bool
    changed: bool
    message: str = ""


@dataclass(slots=True)
class BuildResult:
    """Outcome contract for readmodel build use-case."""

    success: bool
    built: bool
    message: str = ""


@dataclass(slots=True)
class RenderResult:
    """Outcome contract for renderer use-case."""

    success: bool
    rendered: bool
    message: str = ""


@dataclass(slots=True)
class NotifyResult:
    """Outcome contract for notification use-case."""

    success: bool
    sent: bool
    message: str = ""


class SyncUseCase(Protocol):
    """Sync use-case interface."""

    def run(self, ctx: AppContext) -> SyncResult: ...


class BuildReadmodelUseCase(Protocol):
    """Readmodel build use-case interface."""

    def run(self, ctx: AppContext) -> BuildResult: ...


class RenderUseCase(Protocol):
    """Sheet render use-case interface."""

    def run(self, ctx: AppContext) -> RenderResult: ...


class NotifyUseCase(Protocol):
    """Morning notification use-case interface."""

    def run(self, ctx: AppContext) -> NotifyResult: ...


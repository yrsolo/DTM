"""Canonical timer pipeline runtime (snapshot-engine cutover)."""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any

from src.app.context import AppContext
from src.contexts.snapshot.public import get_snapshot_engine as _get_snapshot_engine


build_snapshot_engine = _get_snapshot_engine


@dataclass(frozen=True)
class RunRequest:
    mode: str
    force_refresh: bool
    task_source: Any


@dataclass(frozen=True)
class PipelineResult:
    sync_deferred: bool
    readmodel_deferred: bool
    ttl_skip: bool


class TimerPipeline:
    """Snapshot update pipeline using AppContext dependencies."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def run(self, request: RunRequest) -> PipelineResult:
        mode = str(request.mode).strip().lower()
        if mode not in {"timer", "test", "sync-only"}:
            return PipelineResult(sync_deferred=False, readmodel_deferred=False, ttl_skip=False)

        try:
            engine = build_snapshot_engine(self._ctx)
            result = engine.update(task_source=request.task_source, force=bool(request.force_refresh))
            self._ctx.log(
                "snapshot_update="
                f"source_id={result.source_id} "
                f"source_hash={result.source_hash} "
                f"changed={result.changed} "
                f"raw_written={result.raw_written} "
                f"prep_written={result.prep_written}"
            )
            print("migration_defer_status sync_deferred=False readmodel_deferred=False")
            return PipelineResult(sync_deferred=False, readmodel_deferred=False, ttl_skip=not result.changed)
        except Exception as exc:
            safe_error = str(exc).encode("ascii", "backslashreplace").decode("ascii")
            self._ctx.log(f"snapshot_update_error={safe_error}")
            safe_trace = traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii")
            self._ctx.log(f"snapshot_update_trace={safe_trace}")
            print("migration_defer_status sync_deferred=True readmodel_deferred=False")
            return PipelineResult(sync_deferred=True, readmodel_deferred=False, ttl_skip=False)

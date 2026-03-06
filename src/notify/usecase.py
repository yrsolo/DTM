from __future__ import annotations

from src.snapshot_engine.engine import SnapshotEngine

from .model import ReminderRequest, ReminderResult


class ReminderUseCase:
    """Pure selection + grouping. Does not format or send."""

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine

    def run(self, req: ReminderRequest) -> ReminderResult:
        raise NotImplementedError

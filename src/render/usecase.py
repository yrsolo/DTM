from __future__ import annotations

from src.snapshot_engine.engine import SnapshotEngine

from .model import RenderPlan, RenderRequest


class RenderUseCase:
    """Pure transformation: snapshot query result into render plan."""

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine

    def build_plan(self, req: RenderRequest) -> RenderPlan:
        raise NotImplementedError

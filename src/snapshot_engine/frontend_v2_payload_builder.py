from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.snapshot_engine.model import FrontendV2Query, PrepSnapshot, TaskView


@dataclass(frozen=True)
class FrontendV2Payload:
    """Exact external payload shape: meta + filters + summary + entities + tasks."""

    data: dict[str, Any]


class FrontendV2PayloadBuilder:
    """Build API v2 payload directly from PrepSnapshot without legacy builders."""

    def build(self, snap: PrepSnapshot, q: FrontendV2Query, selected: list[TaskView]) -> FrontendV2Payload:
        raise NotImplementedError

    def build_meta(self, snap: PrepSnapshot, q: FrontendV2Query) -> dict[str, Any]:
        raise NotImplementedError

    def build_filters_block(self, q: FrontendV2Query) -> dict[str, Any]:
        raise NotImplementedError

    def build_entities(self, snap: PrepSnapshot, q: FrontendV2Query, selected: list[TaskView]) -> dict[str, Any]:
        raise NotImplementedError

    def build_tasks(self, selected: list[TaskView]) -> list[dict[str, Any]]:
        raise NotImplementedError

    def build_summary(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError

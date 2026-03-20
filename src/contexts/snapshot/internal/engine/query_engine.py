"""Snapshot query engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from src.contexts.snapshot.internal.engine.frontend_v2_payload_builder import FrontendV2PayloadBuilder
from src.contexts.snapshot.internal.engine.model import PrepSnapshot


@dataclass(frozen=True)
class FrontendV2Query:
    statuses: list[str]
    designer: str
    limit: int
    include_people: bool
    window_enabled: bool
    window_start: date | None
    window_end: date | None
    window_mode: str = "intersects"


class SnapshotQueryEngine:
    def __init__(
        self,
        *,
        env_name: str,
        source_sheet_name: str,
        frontend_builder: FrontendV2PayloadBuilder | None = None,
    ) -> None:
        self._env_name = env_name
        self._source_sheet_name = source_sheet_name
        self._frontend_builder = frontend_builder or FrontendV2PayloadBuilder()

    def query_frontend_v2(self, snap: PrepSnapshot, query: FrontendV2Query) -> dict[str, Any]:
        normalized_query = FrontendV2Query(
            statuses=list(query.statuses),
            designer=str(query.designer),
            limit=int(query.limit),
            include_people=bool(query.include_people),
            window_enabled=bool(query.window_enabled),
            window_start=query.window_start if query.window_enabled else None,
            window_end=query.window_end if query.window_enabled else None,
            window_mode=str(query.window_mode or "intersects"),
        )
        selected = self._frontend_builder.select_tasks(snap, normalized_query)
        return self._frontend_builder.build(
            snap,
            normalized_query,
            selected,
            env_name=self._env_name,
            source_sheet_name=self._source_sheet_name,
        ).data

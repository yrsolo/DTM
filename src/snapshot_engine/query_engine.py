"""Snapshot query engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from types import SimpleNamespace
from typing import Any

import pandas as pd

from core.api_payload_v2 import build_frontend_api_payload_v2
from core.models.people import Person
from src.snapshot_engine.model import PrepSnapshot, TaskSheet


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


def _to_task_object(sheet: TaskSheet) -> Any:
    timing = {pd.Timestamp(key): list(value) for key, value in sheet.timing.items() if key}
    min_date = min(timing.keys()) if timing else None
    max_date = max(timing.keys()) if timing else None
    return SimpleNamespace(
        id=sheet.task_id,
        name=sheet.title,
        designer=sheet.owner_id,
        status=sheet.history,
        history=sheet.history,
        color_status=sheet.status,
        brand=sheet.brand,
        format_=sheet.format_,
        project_name=sheet.group_id,
        customer=sheet.customer,
        raw_timing=sheet.raw_timing,
        timing=timing,
        min_date=min_date,
        max_date=max_date,
    )


class SnapshotQueryEngine:
    def __init__(self, *, env_name: str, source_sheet_name: str) -> None:
        self._env_name = env_name
        self._source_sheet_name = source_sheet_name

    @staticmethod
    def _build_people(tasks: list[Any]) -> list[Person]:
        names: dict[str, Person] = {}
        for task in tasks:
            for raw_name in str(getattr(task, "designer", "")).split("\n"):
                name = str(raw_name).strip()
                if not name:
                    continue
                if name in names:
                    continue
                names[name] = Person(
                    person_id=name,
                    name=name,
                    email="",
                    position="designer",
                    telegram_id="",
                    chat_id="",
                    info="",
                    vacation="",
                )
        return sorted(names.values(), key=lambda item: item.id)

    def query_frontend_v2(self, snap: PrepSnapshot, query: FrontendV2Query) -> dict[str, Any]:
        tasks = [_to_task_object(view.sheet) for view in snap.tasks_by_id.values()]
        people = self._build_people(tasks)
        payload = build_frontend_api_payload_v2(
            tasks=tasks,
            people=people,
            env_name=self._env_name,
            source_sheet_name=self._source_sheet_name,
            statuses=list(query.statuses),
            limit=int(query.limit),
            include_people=bool(query.include_people),
            designer_filter=str(query.designer),
            window_start=query.window_start if query.window_enabled else None,
            window_end=query.window_end if query.window_enabled else None,
            window_mode=query.window_mode,
            generated_at=snap.built_at_utc if snap.built_at_utc.tzinfo else snap.built_at_utc.replace(tzinfo=timezone.utc),
            synced_at=datetime.now(timezone.utc),
        )
        payload.setdefault("meta", {})
        payload["meta"]["sourceHash"] = snap.raw_source_hash
        payload["meta"]["sourceId"] = snap.source_id
        payload["meta"]["readmodelSource"] = "s3_snapshot"
        payload["meta"]["queryFilterApplied"] = True
        payload["meta"]["queryFilterNote"] = ""
        return payload

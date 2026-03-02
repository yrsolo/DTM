"""Sheets -> operational YDB sync service with source-range hash gate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from typing import Any

from src.adapters.ydb.operational_repo import OperationalTaskRepo


def stable_json_hash(values: Any) -> str:
    """Hash source-range values with stable serialization."""
    encoded = json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _to_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


@dataclass(slots=True)
class SyncRunResult:
    source_id: str
    source_hash: str
    previous_hash: str | None
    no_changes: bool
    tasks_upserted: int
    milestones_upserted: int


class YdbSyncService:
    """Sync normalized tasks into YDB operational tables."""

    def __init__(self, repo: OperationalTaskRepo) -> None:
        self.repo = repo

    def run(self, *, source_id: str, source_range_values: Any, normalized_tasks: list[dict[str, Any]]) -> SyncRunResult:
        source_hash = stable_json_hash(source_range_values)
        state = self.repo.get_sync_state(source_id)
        previous_hash = state.source_hash if state is not None else None
        if previous_hash == source_hash:
            return SyncRunResult(
                source_id=source_id,
                source_hash=source_hash,
                previous_hash=previous_hash,
                no_changes=True,
                tasks_upserted=0,
                milestones_upserted=0,
            )

        task_rows: list[dict[str, Any]] = []
        milestones_total = 0
        for task in normalized_tasks:
            task_id = str(task.get("task_id", task.get("id", ""))).strip()
            if not task_id:
                continue
            milestones = task.get("milestones", [])
            timing_fallback = task.get("timing", [])
            if not milestones and isinstance(timing_fallback, list):
                milestones = [
                    {
                        "idx": idx,
                        "type": str(item.get("type", "unknown")).strip() if isinstance(item, dict) else "unknown",
                        "planned": item.get("date") if isinstance(item, dict) else None,
                        "status": "planned",
                    }
                    for idx, item in enumerate(timing_fallback)
                ]

            min_date = None
            max_date = None
            if isinstance(milestones, list):
                for milestone in milestones:
                    planned = _to_date(milestone.get("planned") if isinstance(milestone, dict) else None)
                    if planned is None:
                        continue
                    min_date = planned if min_date is None or planned < min_date else min_date
                    max_date = planned if max_date is None or planned > max_date else max_date

            task_rows.append(
                {
                    "task_id": task_id,
                    "title": str(task.get("title", task.get("name", ""))).strip(),
                    "owner_id": str(task.get("owner_id", task.get("designer", ""))).strip(),
                    "group_id": str(task.get("group_id", task.get("project_name", ""))).strip(),
                    "status": str(task.get("status", task.get("color_status", "unknown"))).strip().lower() or "unknown",
                    "start_date": task.get("start_date") or min_date,
                    "end_date": task.get("end_date") or max_date,
                    "next_due_date": task.get("next_due_date") or min_date,
                    "tags": task.get("tags", []),
                    "links": task.get("links", {}),
                    "task_hash": task.get("task_hash"),
                    "task_revision": task.get("task_revision", 0),
                    "raw_payload": task,
                }
            )
            milestones_total += self.repo.replace_task_milestones(task_id, milestones if isinstance(milestones, list) else [])

        tasks_upserted = self.repo.upsert_tasks_batch(task_rows)
        self.repo.set_sync_state(source_id=source_id, source_hash=source_hash)
        return SyncRunResult(
            source_id=source_id,
            source_hash=source_hash,
            previous_hash=previous_hash,
            no_changes=False,
            tasks_upserted=tasks_upserted,
            milestones_upserted=milestones_total,
        )


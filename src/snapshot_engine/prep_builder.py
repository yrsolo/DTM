"""Prep snapshot builder."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from src.snapshot_engine.interfaces import ExtraStore
from src.snapshot_engine.model import PrepIndexes, PrepSnapshot, RawSnapshot, TaskView


class PrepBuilder:
    def __init__(self, extra_store: ExtraStore) -> None:
        self._extra_store = extra_store

    def build(self, raw: RawSnapshot) -> PrepSnapshot:
        task_ids = sorted(raw.tasks_by_id.keys())
        extras = self._extra_store.get_many(task_ids)
        for task_id in list(extras.keys()):
            if task_id not in raw.tasks_by_id:
                self._extra_store.mark_orphaned(task_id, orphaned=True)

        tasks_by_id: dict[str, TaskView] = {}
        for task_id, sheet in raw.tasks_by_id.items():
            tasks_by_id[task_id] = TaskView(sheet=sheet, extra=extras.get(task_id))

        by_status: dict[str, list[str]] = defaultdict(list)
        by_owner: dict[str, list[str]] = defaultdict(list)
        for task_id, view in tasks_by_id.items():
            by_status[view.sheet.status].append(task_id)
            if view.sheet.owner_id:
                by_owner[view.sheet.owner_id].append(task_id)

        return PrepSnapshot(
            source_id=raw.source_id,
            raw_source_hash=raw.source_hash,
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id=tasks_by_id,
            indexes=PrepIndexes(
                by_status={k: sorted(v) for k, v in by_status.items()},
                by_owner={k: sorted(v) for k, v in by_owner.items()},
            ),
        )

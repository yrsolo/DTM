"""Prep snapshot builder."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from time import perf_counter

from src.snapshot_engine.interfaces import ExtraStore
from src.snapshot_engine.model import ExtraSnapshot, PrepBuildResult, PrepIndexes, PrepSnapshot, RawSnapshot, TaskExtra, TaskView


class PrepBuilder:
    def __init__(self, extra_store: ExtraStore) -> None:
        self._extra_store = extra_store

    def build(self, raw: RawSnapshot) -> PrepBuildResult:
        total_started = perf_counter()

        extra_load_started = perf_counter()
        extra_snapshot = self._extra_store.get_snapshot()
        extra_load_ms = (perf_counter() - extra_load_started) * 1000.0

        orphan_started = perf_counter()
        extra_snapshot, extra_snapshot_changed = self._reconcile_orphans(raw=raw, snapshot=extra_snapshot)
        orphan_reconcile_ms = (perf_counter() - orphan_started) * 1000.0
        if extra_snapshot_changed:
            self._extra_store.put_snapshot(extra_snapshot)

        task_view_started = perf_counter()
        tasks_by_id: dict[str, TaskView] = {}
        items_by_task_id = extra_snapshot.items_by_task_id
        for task_id, sheet in raw.tasks_by_id.items():
            tasks_by_id[task_id] = TaskView(sheet=sheet, extra=items_by_task_id.get(task_id))
        task_view_build_ms = (perf_counter() - task_view_started) * 1000.0

        index_started = perf_counter()
        by_status: dict[str, list[str]] = defaultdict(list)
        by_owner: dict[str, list[str]] = defaultdict(list)
        for task_id, view in tasks_by_id.items():
            by_status[view.sheet.status].append(task_id)
            if view.sheet.owner_id:
                by_owner[view.sheet.owner_id].append(task_id)
        prep_index_build_ms = (perf_counter() - index_started) * 1000.0

        return PrepBuildResult(
            prep=PrepSnapshot(
                source_id=raw.source_id,
                raw_source_hash=raw.source_hash,
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id=tasks_by_id,
                indexes=PrepIndexes(
                    by_status={k: sorted(v) for k, v in by_status.items()},
                    by_owner={k: sorted(v) for k, v in by_owner.items()},
                ),
            ),
            timings_ms={
                "extra_load_ms": extra_load_ms,
                "orphan_reconcile_ms": orphan_reconcile_ms,
                "task_view_build_ms": task_view_build_ms,
                "prep_index_build_ms": prep_index_build_ms,
                "prep_build_total_ms": (perf_counter() - total_started) * 1000.0,
            },
            extra_snapshot_changed=extra_snapshot_changed,
        )

    @staticmethod
    def _reconcile_orphans(*, raw: RawSnapshot, snapshot: ExtraSnapshot) -> tuple[ExtraSnapshot, bool]:
        known_ids = set(raw.tasks_by_id.keys())
        changed = False
        items_by_task_id = dict(snapshot.items_by_task_id)
        for task_id, extra in list(items_by_task_id.items()):
            should_be_orphaned = task_id not in known_ids
            if bool(extra.orphaned) == should_be_orphaned:
                continue
            changed = True
            items_by_task_id[task_id] = TaskExtra(
                task_id=extra.task_id,
                orphaned=should_be_orphaned,
                updated_at_utc=datetime.now(timezone.utc),
                attachments=list(extra.attachments),
                docs=list(extra.docs),
                links=list(extra.links),
                notes=str(extra.notes),
                artifacts=list(extra.artifacts),
            )
        if not changed:
            return snapshot, False
        return (
            ExtraSnapshot(
                version=snapshot.version,
                updated_at_utc=datetime.now(timezone.utc),
                items_by_task_id=items_by_task_id,
            ),
            True,
        )

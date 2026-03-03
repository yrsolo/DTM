"""Sheets -> operational YDB sync service with source-range hash gate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _content_hash_for_task(task: dict[str, Any], milestones: list[dict[str, Any]]) -> str:
    basis = {
        "title": str(task.get("title", task.get("name", ""))).strip(),
        "brand": str(task.get("brand", "")).strip(),
        "format_": str(task.get("format_", "")).strip(),
        "customer": str(task.get("customer", "")).strip(),
        "owner_id": str(task.get("owner_id", task.get("designer", ""))).strip(),
        "group_id": str(task.get("group_id", task.get("project_name", ""))).strip(),
        "raw_timing": str(task.get("raw_timing", "")).strip(),
        "milestones": [
            {
                "type": str(item.get("type", "")).strip(),
                "planned": str(item.get("planned") or item.get("planned_date") or "").strip(),
                "actual": str(item.get("actual") or item.get("actual_date") or "").strip(),
                "status": str(item.get("status", "")).strip(),
                "raw_text": str(item.get("raw_text", "")).strip(),
            }
            for item in milestones
        ],
    }
    encoded = json.dumps(basis, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _ensure_start_milestone(
    *,
    milestones: list[dict[str, Any]],
    now_utc: datetime,
) -> list[dict[str, Any]]:
    normalized = list(milestones)
    milestone_dates = [
        _to_date(item.get("planned") if isinstance(item, dict) else None) for item in normalized
    ]
    milestone_dates = [item for item in milestone_dates if item is not None]
    earliest = min(milestone_dates) if milestone_dates else None
    created_at_date = now_utc.date() if earliest is None else min(now_utc.date(), earliest)
    need_start = earliest is None or created_at_date < earliest
    if need_start:
        normalized.append(
            {
                "idx": -1,
                "type": "start",
                "planned": created_at_date.isoformat(),
                "actual": None,
                "status": "planned",
                "raw_text": "start",
            }
        )
    normalized.sort(
        key=lambda item: (
            _to_date(item.get("planned") if isinstance(item, dict) else None) is None,
            _to_date(item.get("planned") if isinstance(item, dict) else None) or date.max,
            str(item.get("type", "")).strip(),
        )
    )
    for index, item in enumerate(normalized):
        if isinstance(item, dict):
            item["idx"] = index
    return normalized


@dataclass(slots=True)
class SyncRunResult:
    source_id: str
    preflight_hash_50: str
    source_hash_full: str
    previous_preflight_hash_50: str | None
    previous_source_hash_full: str | None
    no_changes: bool
    full_sync_performed: bool
    forced_refresh: bool
    tasks_upserted: int
    milestones_upserted: int
    ydb_queries_count: int
    ydb_error_code: str


class YdbSyncService:
    """Sync normalized tasks into YDB operational tables."""

    def __init__(self, repo: OperationalTaskRepo, *, write_legacy_milestones: bool = False) -> None:
        self.repo = repo
        self.write_legacy_milestones = bool(write_legacy_milestones)

    def run(
        self,
        *,
        source_id: str,
        preflight_range_values: Any,
        source_range_values: Any,
        normalized_tasks: list[dict[str, Any]],
        force_refresh: bool = False,
        full_sync_interval_hours: int = 24,
    ) -> SyncRunResult:
        preflight_hash_50 = stable_json_hash(preflight_range_values)
        source_hash_full = stable_json_hash(source_range_values)
        now_utc = _utc_now()
        state = self.repo.get_sync_state(source_id)
        previous_preflight = state.preflight_hash_50 if state is not None else None
        previous_full = state.source_hash_full if state is not None else None

        full_sync_stale = True
        if state is not None and state.last_full_sync_at_utc is not None:
            full_sync_stale = now_utc - state.last_full_sync_at_utc >= timedelta(hours=max(full_sync_interval_hours, 1))
        preflight_changed = previous_preflight != preflight_hash_50
        full_sync_required = force_refresh or preflight_changed or full_sync_stale or state is None

        if not full_sync_required:
            self.repo.set_sync_state(
                source_id=source_id,
                preflight_hash_50=preflight_hash_50,
                source_hash_full=previous_full or source_hash_full,
                synced_at_utc=now_utc,
                last_full_sync_at_utc=state.last_full_sync_at_utc if state is not None else now_utc,
                last_success_at_utc=now_utc,
            )
            return SyncRunResult(
                source_id=source_id,
                preflight_hash_50=preflight_hash_50,
                source_hash_full=source_hash_full,
                previous_preflight_hash_50=previous_preflight,
                previous_source_hash_full=previous_full,
                no_changes=True,
                full_sync_performed=False,
                forced_refresh=force_refresh,
                tasks_upserted=0,
                milestones_upserted=0,
                ydb_queries_count=self.repo.client.stats.ydb_queries_count,
                ydb_error_code=self.repo.client.stats.error_code,
            )

        if not force_refresh and previous_full == source_hash_full:
            self.repo.set_sync_state(
                source_id=source_id,
                preflight_hash_50=preflight_hash_50,
                source_hash_full=source_hash_full,
                synced_at_utc=now_utc,
                last_full_sync_at_utc=now_utc,
                last_success_at_utc=now_utc,
            )
            return SyncRunResult(
                source_id=source_id,
                preflight_hash_50=preflight_hash_50,
                source_hash_full=source_hash_full,
                previous_preflight_hash_50=previous_preflight,
                previous_source_hash_full=previous_full,
                no_changes=True,
                full_sync_performed=True,
                forced_refresh=force_refresh,
                tasks_upserted=0,
                milestones_upserted=0,
                ydb_queries_count=self.repo.client.stats.ydb_queries_count,
                ydb_error_code=self.repo.client.stats.error_code,
            )

        task_rows: list[dict[str, Any]] = []
        milestones_by_task: dict[str, list[dict[str, Any]]] = {}
        milestones_versions_by_task: dict[tuple[str, int], list[dict[str, Any]]] = {}
        changed_version_tasks: dict[str, int] = {}
        pending_archives: list[tuple[str, int]] = []
        existing_rows = {str(row.get("task_id", "")).strip(): row for row in self.repo.list_tasks() if str(row.get("task_id", "")).strip()}

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

            milestones = _ensure_start_milestone(milestones=milestones if isinstance(milestones, list) else [], now_utc=now_utc)
            min_date = None
            max_date = None
            if isinstance(milestones, list):
                for milestone in milestones:
                    planned = _to_date(milestone.get("planned") if isinstance(milestone, dict) else None)
                    if planned is None:
                        continue
                    min_date = planned if min_date is None or planned < min_date else min_date
                    max_date = planned if max_date is None or planned > max_date else max_date

            content_hash = _content_hash_for_task(task, milestones if isinstance(milestones, list) else [])
            existing_row = existing_rows.get(task_id)
            previous_hash = str(existing_row.get("task_hash", "")).strip() if isinstance(existing_row, dict) else ""
            previous_version = int(existing_row.get("task_revision", 0) or 0) if isinstance(existing_row, dict) else 0

            if existing_row is None:
                task_revision = 1
                create_new_version = True
            elif force_refresh:
                task_revision = max(previous_version, 1)
                create_new_version = False
            elif previous_hash != content_hash:
                task_revision = max(previous_version, 0) + 1
                create_new_version = True
            else:
                task_revision = max(previous_version, 1)
                create_new_version = False

            if create_new_version and not force_refresh:
                self.repo.upsert_task_version(
                    task_id=task_id,
                    version=task_revision,
                    status="active",
                    content_hash=content_hash,
                    payload_json=json.dumps(task, ensure_ascii=False, sort_keys=True),
                    created_at_utc=now_utc,
                )
                changed_version_tasks[task_id] = task_revision
                if previous_version > 0:
                    pending_archives.append((task_id, previous_version))

            task_rows.append(
                {
                    "task_id": task_id,
                    "title": str(task.get("title", task.get("name", ""))).strip(),
                    "brand": str(task.get("brand", "")).strip(),
                    "format_": str(task.get("format_", "")).strip(),
                    "customer": str(task.get("customer", "")).strip(),
                    "raw_timing": str(task.get("raw_timing", "")).strip(),
                    "owner_id": str(task.get("owner_id", task.get("designer", ""))).strip(),
                    "group_id": str(task.get("group_id", task.get("project_name", ""))).strip(),
                    "status": str(task.get("status", task.get("color_status", "unknown"))).strip().lower() or "unknown",
                    "start_date": task.get("start_date") or min_date,
                    "end_date": task.get("end_date") or max_date,
                    "next_due_date": task.get("next_due_date") or min_date,
                    "tags": task.get("tags", []),
                    "links": task.get("links", {}),
                    "task_hash": content_hash if (create_new_version or not force_refresh or not previous_hash) else previous_hash,
                    "task_revision": task_revision,
                    "raw_payload": task,
                }
            )
            milestones_by_task[task_id] = milestones if isinstance(milestones, list) else []
            if create_new_version and not force_refresh:
                version_rows = milestones if isinstance(milestones, list) else []
                if not version_rows:
                    raise RuntimeError("milestones_write_empty")
                milestones_versions_by_task[(task_id, task_revision)] = version_rows

        if self.write_legacy_milestones:
            milestones_total = self.repo.replace_task_milestones_bulk(milestones_by_task)
        else:
            milestones_total = 0
            print("legacy_milestones_write=skipped reason=disabled")

        if milestones_versions_by_task:
            milestones_written = self.repo.upsert_task_milestones_versions_bulk(milestones_versions_by_task)
            if milestones_written <= 0:
                raise RuntimeError("milestones_write_empty")
        tasks_upserted = self.repo.upsert_tasks_batch(task_rows)

        if changed_version_tasks:
            current_rows = {
                str(row.get("task_id", "")).strip(): int(row.get("current_version", row.get("task_revision", 0)) or 0)
                for row in self.repo.list_tasks()
                if str(row.get("task_id", "")).strip()
            }
            missing_version_head = [
                task_id for task_id, expected_version in changed_version_tasks.items()
                if current_rows.get(task_id, 0) != expected_version
            ]
            if missing_version_head:
                raise RuntimeError("current_version_missing_after_sync")

            versioned_rows = self.repo.list_milestones_for_versions(task_versions=changed_version_tasks)
            rows_by_key: dict[tuple[str, int], int] = {}
            for item in versioned_rows:
                key = (str(item.get("task_id", "")).strip(), int(item.get("version", 0) or 0))
                rows_by_key[key] = rows_by_key.get(key, 0) + 1
            missing_milestones = [
                task_id
                for task_id, version in changed_version_tasks.items()
                if rows_by_key.get((task_id, version), 0) <= 0
            ]
            if missing_milestones:
                raise RuntimeError("milestones_current_version_missing")

        for task_id, previous_version in pending_archives:
            self.repo.archive_task_version(task_id=task_id, version=previous_version)

        self.repo.set_sync_state(
            source_id=source_id,
            preflight_hash_50=preflight_hash_50,
            source_hash_full=source_hash_full,
            synced_at_utc=now_utc,
            last_full_sync_at_utc=now_utc,
            last_success_at_utc=now_utc,
        )
        return SyncRunResult(
            source_id=source_id,
            preflight_hash_50=preflight_hash_50,
            source_hash_full=source_hash_full,
            previous_preflight_hash_50=previous_preflight,
            previous_source_hash_full=previous_full,
            no_changes=False,
            full_sync_performed=True,
            forced_refresh=force_refresh,
            tasks_upserted=tasks_upserted,
            milestones_upserted=milestones_total,
            ydb_queries_count=self.repo.client.stats.ydb_queries_count,
            ydb_error_code=self.repo.client.stats.error_code,
        )

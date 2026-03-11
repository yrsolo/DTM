"""Migrate milestones into versioned table (task_id, version) with fallback logic."""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from src.adapters.ydb.operational_repo import OperationalTaskRepo


@dataclass(slots=True)
class MigrationStats:
    tasks_total: int
    tasks_with_current_version: int
    tasks_from_legacy_table: int
    tasks_from_raw_payload: int
    rows_prepared: int
    rows_written: int
    verify_sample_size: int
    verify_matches: int
    verify_mismatches: int


def _group_by_task(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        task_id = str(row.get("task_id", "")).strip()
        if not task_id:
            continue
        grouped[task_id].append(row)
    for items in grouped.values():
        items.sort(key=lambda item: int(item.get("idx", 0) or 0))
    return dict(grouped)


def _chunk(items: list[str], size: int = 20) -> list[list[str]]:
    if size <= 0:
        return [items]
    return [items[index : index + size] for index in range(0, len(items), size)]


def _extract_from_raw_payload(raw_payload_text: str) -> list[dict[str, Any]]:
    text = str(raw_payload_text or "").strip()
    if not text:
        return []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    milestones = payload.get("milestones", []) if isinstance(payload, dict) else []
    if not isinstance(milestones, list):
        return []
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(milestones):
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "idx": int(item.get("idx", idx)),
                "type": str(item.get("type", "")).strip() or "unknown",
                "planned_date": item.get("planned_date", item.get("planned")),
                "actual_date": item.get("actual_date", item.get("actual")),
                "status": str(item.get("status", "unknown")).strip() or "unknown",
                "raw_text": str(item.get("raw_text", "")).strip() or None,
                "confidence": float(item.get("confidence", 0.0) or 0.0),
                "inference_rule": str(item.get("inference_rule", "")).strip() or None,
            }
        )
    return normalized


def _resolve_ydb_args(endpoint: str, database: str) -> tuple[str, str]:
    load_dotenv()
    resolved_endpoint = str(endpoint or os.getenv("YDB_ENDPOINT", "")).strip()
    resolved_database = str(database or os.getenv("YDB_DATABASE", "")).strip()
    if not resolved_endpoint or not resolved_database:
        raise ValueError("YDB endpoint/database must be provided via args or local env for this agent script")
    return resolved_endpoint, resolved_database


def run(*, endpoint: str, database: str, apply: bool) -> MigrationStats:
    repo = OperationalTaskRepo(endpoint=endpoint, database=database, ensure_schema=False)
    tasks = repo.list_tasks()
    tasks_with_versions = {
        str(item.get("task_id", "")).strip(): int(item.get("current_version", item.get("task_revision", 0)) or 0)
        for item in tasks
        if str(item.get("task_id", "")).strip() and int(item.get("current_version", item.get("task_revision", 0)) or 0) > 0
    }
    task_ids = list(tasks_with_versions.keys())

    legacy_rows: list[dict[str, Any]] = []
    for chunk in _chunk(task_ids):
        legacy_rows.extend(repo.list_milestones(task_ids=chunk))
    legacy_by_task = _group_by_task(legacy_rows)

    rows_by_task_version: dict[tuple[str, int], list[dict[str, Any]]] = {}
    tasks_from_legacy = 0
    tasks_from_raw_payload = 0
    raw_payload_map = {str(item.get("task_id", "")).strip(): str(item.get("raw_payload", "{}")) for item in tasks}

    for task_id, version in tasks_with_versions.items():
        version_key = (task_id, int(version))
        candidate_rows = legacy_by_task.get(task_id, [])
        if candidate_rows:
            rows_by_task_version[version_key] = candidate_rows
            tasks_from_legacy += 1
            continue
        fallback_rows = _extract_from_raw_payload(raw_payload_map.get(task_id, "{}"))
        if fallback_rows:
            rows_by_task_version[version_key] = fallback_rows
            tasks_from_raw_payload += 1

    rows_prepared = sum(len(rows) for rows in rows_by_task_version.values())
    rows_written = 0
    if apply and rows_by_task_version:
        rows_written = repo.upsert_task_milestones_versions_bulk(rows_by_task_version)

    verify_sample_size = min(10, len(tasks_with_versions))
    verify_matches = 0
    verify_mismatches = 0
    if verify_sample_size > 0:
        sample_task_ids = sorted(tasks_with_versions.keys())[:verify_sample_size]
        sample_versions = {task_id: tasks_with_versions[task_id] for task_id in sample_task_ids}
        versioned_rows = repo.list_milestones_for_versions(task_versions=sample_versions)
        versioned_by_task = _group_by_task(versioned_rows)
        for task_id in sample_task_ids:
            source_rows = rows_by_task_version.get((task_id, int(tasks_with_versions[task_id])), [])
            source_sig = [
                (str(item.get("type", "")), str(item.get("planned_date") or ""), str(item.get("status", "")))
                for item in source_rows
            ]
            versioned_sig = [
                (str(item.get("type", "")), str(item.get("planned_date") or ""), str(item.get("status", "")))
                for item in versioned_by_task.get(task_id, [])
            ]
            if source_sig == versioned_sig:
                verify_matches += 1
            else:
                verify_mismatches += 1

    return MigrationStats(
        tasks_total=len(tasks),
        tasks_with_current_version=len(tasks_with_versions),
        tasks_from_legacy_table=tasks_from_legacy,
        tasks_from_raw_payload=tasks_from_raw_payload,
        rows_prepared=rows_prepared,
        rows_written=rows_written,
        verify_sample_size=verify_sample_size,
        verify_matches=verify_matches,
        verify_mismatches=verify_mismatches,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate milestones to versioned YDB table")
    parser.add_argument("--endpoint", default="", help="YDB endpoint override")
    parser.add_argument("--database", default="", help="YDB database override")
    parser.add_argument("--apply", action="store_true", help="Write migrated rows into dtm_task_milestones_v")
    args = parser.parse_args()

    endpoint, database = _resolve_ydb_args(args.endpoint, args.database)
    stats = run(endpoint=endpoint, database=database, apply=args.apply)
    print(f"tasks_total={stats.tasks_total}")
    print(f"tasks_with_current_version={stats.tasks_with_current_version}")
    print(f"tasks_from_legacy_table={stats.tasks_from_legacy_table}")
    print(f"tasks_from_raw_payload={stats.tasks_from_raw_payload}")
    print(f"rows_prepared={stats.rows_prepared}")
    print(f"rows_written={stats.rows_written}")
    print(f"verify_sample_size={stats.verify_sample_size}")
    print(f"verify_matches={stats.verify_matches}")
    print(f"verify_mismatches={stats.verify_mismatches}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

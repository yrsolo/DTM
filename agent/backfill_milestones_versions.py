"""Backfill dtm_task_milestones_v from legacy dtm_task_milestones for current task versions."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from config.constants import YDB_DATABASE, YDB_ENDPOINT
from src.adapters.ydb.operational_repo import OperationalTaskRepo


@dataclass(slots=True)
class BackfillStats:
    tasks_total: int
    tasks_with_versions: int
    tasks_with_legacy_milestones: int
    rows_prepared: int
    rows_written: int
    verify_sample_size: int
    verify_matches: int
    verify_mismatches: int


def _chunk(items: list[str], size: int) -> list[list[str]]:
    if size <= 0:
        return [items]
    return [items[index : index + size] for index in range(0, len(items), size)]


def _group_by_task(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        task_id = str(row.get("task_id", "")).strip()
        if not task_id:
            continue
        grouped[task_id].append(row)
    for task_rows in grouped.values():
        task_rows.sort(key=lambda item: int(item.get("idx", 0) or 0))
    return dict(grouped)


def _milestone_signature(rows: list[dict[str, Any]]) -> list[tuple[str, str, str, str]]:
    signature: list[tuple[str, str, str, str]] = []
    for item in rows:
        signature.append(
            (
                str(item.get("type", "")).strip(),
                str(item.get("planned_date") or "").strip(),
                str(item.get("actual_date") or "").strip(),
                str(item.get("status", "")).strip(),
            )
        )
    return signature


def run(*, apply: bool, verify_sample_size: int) -> BackfillStats:
    repo = OperationalTaskRepo(endpoint=YDB_ENDPOINT, database=YDB_DATABASE, ensure_schema=False)
    tasks = repo.list_tasks()
    task_versions = {
        str(row.get("task_id", "")).strip(): int(row.get("current_version", row.get("task_revision", 0)) or 0)
        for row in tasks
        if str(row.get("task_id", "")).strip()
    }
    task_versions = {task_id: version for task_id, version in task_versions.items() if version > 0}

    task_ids = list(task_versions.keys())
    legacy_rows: list[dict[str, Any]] = []
    for task_ids_chunk in _chunk(task_ids, 20):
        legacy_rows.extend(repo.list_milestones(task_ids=task_ids_chunk))
    legacy_by_task = _group_by_task(legacy_rows)

    payload_by_task_version: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for task_id, version in task_versions.items():
        rows = legacy_by_task.get(task_id, [])
        if rows:
            payload_by_task_version[(task_id, version)] = rows

    rows_prepared = sum(len(rows) for rows in payload_by_task_version.values())
    rows_written = 0
    if apply and payload_by_task_version:
        rows_written = repo.upsert_task_milestones_versions_bulk(payload_by_task_version)

    verify_sample = max(0, verify_sample_size)
    verify_matches = 0
    verify_mismatches = 0
    if verify_sample > 0 and task_versions:
        sampled_task_ids = sorted(task_versions.keys())[:verify_sample]
        sampled_versions = {task_id: task_versions[task_id] for task_id in sampled_task_ids}
        versioned_rows = repo.list_milestones_for_versions(task_versions=sampled_versions)
        versioned_by_task = _group_by_task(versioned_rows)
        for task_id in sampled_task_ids:
            legacy_sig = _milestone_signature(legacy_by_task.get(task_id, []))
            versioned_sig = _milestone_signature(versioned_by_task.get(task_id, []))
            if legacy_sig == versioned_sig:
                verify_matches += 1
            else:
                verify_mismatches += 1

    return BackfillStats(
        tasks_total=len(tasks),
        tasks_with_versions=len(task_versions),
        tasks_with_legacy_milestones=len(legacy_by_task),
        rows_prepared=rows_prepared,
        rows_written=rows_written,
        verify_sample_size=verify_sample,
        verify_matches=verify_matches,
        verify_mismatches=verify_mismatches,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill dtm_task_milestones_v from legacy milestones table")
    parser.add_argument("--apply", action="store_true", help="Write backfill rows to dtm_task_milestones_v")
    parser.add_argument(
        "--verify-sample-size",
        type=int,
        default=5,
        help="Compare legacy/versioned milestones signatures for first N task_ids after run",
    )
    args = parser.parse_args()

    stats = run(apply=args.apply, verify_sample_size=args.verify_sample_size)
    print(f"tasks_total={stats.tasks_total}")
    print(f"tasks_with_versions={stats.tasks_with_versions}")
    print(f"tasks_with_legacy_milestones={stats.tasks_with_legacy_milestones}")
    print(f"rows_prepared={stats.rows_prepared}")
    print(f"rows_written={stats.rows_written}")
    print(f"verify_sample_size={stats.verify_sample_size}")
    print(f"verify_matches={stats.verify_matches}")
    print(f"verify_mismatches={stats.verify_mismatches}")
    if stats.verify_mismatches > 0:
        print("verify_ok=false")
        return 1
    print("verify_ok=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

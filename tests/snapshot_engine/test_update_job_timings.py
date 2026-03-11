from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.snapshot_engine.model import PrepBuildResult, PrepIndexes, PrepSnapshot, RawSnapshot, SheetSnapshot, TaskSheet
from src.snapshot_engine.update_job import UpdateJob


class _Source:
    source_id = "sheet:test"
    source_sheet_name = "Test"

    def fetch_snapshot(self, worksheet_range: str) -> SheetSnapshot:  # noqa: ARG002
        return SheetSnapshot(worksheet_range="A1:Z2000", values=[["id"]], colors=[])

    def build_tasks(self, full_snapshot: SheetSnapshot) -> list[object]:  # noqa: ARG002
        return [object()]


class _Hasher:
    def hash_sheet_snapshot(self, snapshot: SheetSnapshot) -> str:  # noqa: ARG002
        return "hash-1"


class _Normalizer:
    def normalize(self, *, source_id: str, source_hash: str, snapshot: SheetSnapshot, tasks: list[object]) -> RawSnapshot:  # noqa: ARG002
        return RawSnapshot(
            source_id=source_id,
            source_hash=source_hash,
            fetched_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "t1": TaskSheet(
                    task_id="t1",
                    title="Task",
                    owner_id="Designer",
                    group_id="Group",
                    brand="Brand",
                    format_="Format",
                    customer="Customer",
                    raw_timing="raw",
                    status="work",
                    history="history",
                    timing={"2026-03-09": ["start"]},
                    milestones=[],
                )
            },
        )


class _RawCache:
    def __init__(self, current=None) -> None:
        self.current = current

    def get(self):
        return self.current

    def put(self, raw) -> None:
        self.current = raw


class _PrepCache:
    def __init__(self, current=None) -> None:
        self.current = current

    def get(self):
        return self.current

    def put(self, prep) -> None:
        self.current = prep


class _PrepBuilder:
    def build(self, raw) -> object:  # noqa: ARG002
        return PrepBuildResult(
            prep=PrepSnapshot(
                source_id="sheet:test",
                raw_source_hash="hash-1",
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id={},
                indexes=PrepIndexes(),
            ),
            timings_ms={
                "extra_load_ms": 1.0,
                "orphan_reconcile_ms": 2.0,
                "task_view_build_ms": 3.0,
                "prep_index_build_ms": 4.0,
            },
        )


class UpdateJobTimingsTestCase(unittest.TestCase):
    def test_run_records_step_timings_for_full_refresh(self) -> None:
        job = UpdateJob(
            source=_Source(),
            hasher=_Hasher(),
            normalizer=_Normalizer(),
            raw_cache=_RawCache(),
            prep_cache=_PrepCache(),
            prep_builder=_PrepBuilder(),
        )

        result = job.run(force=False)

        self.assertTrue(result.changed)
        self.assertTrue(result.raw_written)
        self.assertTrue(result.prep_written)
        for key in (
            "fetch_sheet_ms",
            "normalize_ms",
            "build_prep_ms",
            "extra_load_ms",
            "orphan_reconcile_ms",
            "task_view_build_ms",
            "prep_index_build_ms",
            "write_raw_ms",
            "write_prep_ms",
            "total_duration_ms",
        ):
            self.assertIn(key, result.timings_ms)
            self.assertGreaterEqual(float(result.timings_ms[key]), 0.0)

    def test_run_records_only_available_timings_for_nochange_path(self) -> None:
        previous_raw = RawSnapshot(
            source_id="sheet:test",
            source_hash="hash-1",
            fetched_at_utc=datetime.now(timezone.utc),
            tasks_by_id={},
        )
        job = UpdateJob(
            source=_Source(),
            hasher=_Hasher(),
            normalizer=_Normalizer(),
            raw_cache=_RawCache(previous_raw),
            prep_cache=_PrepCache(
                PrepSnapshot(
                    source_id="sheet:test",
                    raw_source_hash="hash-1",
                    built_at_utc=datetime.now(timezone.utc),
                    tasks_by_id={},
                    indexes=PrepIndexes(),
                )
            ),
            prep_builder=_PrepBuilder(),
        )

        result = job.run(force=False)

        self.assertFalse(result.changed)
        self.assertFalse(result.raw_written)
        self.assertFalse(result.prep_written)
        self.assertIn("fetch_sheet_ms", result.timings_ms)
        self.assertIn("total_duration_ms", result.timings_ms)
        self.assertNotIn("normalize_ms", result.timings_ms)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.snapshot_engine.model import PrepSnapshot, PrepIndexes, RawSnapshot, SheetSnapshot, TaskSheet, TaskView
from src.snapshot_engine.update_job import UpdateJob


class _FakeSource:
    source_id = "sheet:test"
    source_sheet_name = "Sheet"

    def fetch_snapshot(self, worksheet_range: str) -> SheetSnapshot:
        return SheetSnapshot(worksheet_range=worksheet_range, values=[["x"]], colors=[])

    def build_tasks(self, full_snapshot: SheetSnapshot):  # noqa: ANN001
        _ = full_snapshot
        return []


class _FakeHasher:
    def hash_sheet_snapshot(self, snapshot: SheetSnapshot) -> str:  # noqa: ANN001
        return "hash"


class _FakeNormalizer:
    def normalize(self, *, source_id, source_hash, snapshot, tasks):  # noqa: ANN001
        _ = snapshot, tasks
        return RawSnapshot(
            source_id=source_id,
            source_hash=source_hash,
            fetched_at_utc=datetime.now(timezone.utc),
            tasks_by_id={},
        )


class _CorruptedRawCache:
    def __init__(self):
        self.put_called = False

    def get(self):
        raise ValueError("corrupted")

    def put(self, raw):  # noqa: ANN001
        self.put_called = True


class _FakePrepCache:
    def __init__(self):
        self.put_called = False

    def get(self):
        return PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="old",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"x": TaskView(sheet=TaskSheet(task_id="x", title="", owner_id="", group_id="", brand="", format_="", customer="", raw_timing="", status="work", history=""))},
            indexes=PrepIndexes(),
        )

    def put(self, prep):  # noqa: ANN001
        self.put_called = True


class _FakePrepBuilder:
    def build(self, raw):  # noqa: ANN001
        return PrepSnapshot(
            source_id=raw.source_id,
            raw_source_hash=raw.source_hash,
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={},
            indexes=PrepIndexes(),
        )


class UpdateJobTestCase(unittest.TestCase):
    def test_corrupted_raw_cache_does_not_block_rebuild(self) -> None:
        raw_cache = _CorruptedRawCache()
        prep_cache = _FakePrepCache()
        job = UpdateJob(
            source=_FakeSource(),
            hasher=_FakeHasher(),
            normalizer=_FakeNormalizer(),
            raw_cache=raw_cache,
            prep_cache=prep_cache,
            prep_builder=_FakePrepBuilder(),
        )

        result = job.run(force=False)

        self.assertTrue(result.changed)
        self.assertTrue(raw_cache.put_called)
        self.assertTrue(prep_cache.put_called)


if __name__ == "__main__":
    unittest.main()

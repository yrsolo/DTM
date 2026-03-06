from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.snapshot_engine.model import PrepSnapshot, RawSnapshot, TaskExtra, TaskSheet
from src.snapshot_engine.prep_builder import PrepBuilder


class _FakeExtraStore:
    def __init__(self, extras: dict[str, TaskExtra] | None = None) -> None:
        self.extras = extras or {}
        self.orphan_calls: list[str] = []

    def get_many(self, task_ids: list[str]) -> dict[str, TaskExtra]:
        return dict(self.extras)

    def upsert(self, extra: TaskExtra) -> None:  # pragma: no cover - protocol completeness
        self.extras[extra.task_id] = extra

    def mark_orphaned(self, task_id: str, orphaned: bool = True) -> None:
        if orphaned:
            self.orphan_calls.append(task_id)


class PrepBuilderTestCase(unittest.TestCase):
    def _sheet(self, task_id: str, status: str, owner: str) -> TaskSheet:
        return TaskSheet(
            task_id=task_id,
            title=task_id,
            owner_id=owner,
            group_id="g",
            brand="b",
            format_="f",
            customer="c",
            raw_timing="",
            status=status,
            history="h",
        )

    def test_build_merges_extras_and_indexes(self) -> None:
        extra = TaskExtra(task_id="t1")
        store = _FakeExtraStore(extras={"t1": extra})
        raw = RawSnapshot(
            source_id="sheet:test",
            source_hash="hash",
            fetched_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "t1": self._sheet("t1", "work", "u1"),
                "t2": self._sheet("t2", "done", "u2"),
            },
        )

        prep: PrepSnapshot = PrepBuilder(store).build(raw)

        self.assertEqual(prep.raw_source_hash, "hash")
        self.assertIn("t1", prep.indexes.by_status["work"])
        self.assertIn("t2", prep.indexes.by_status["done"])
        self.assertIn("t1", prep.indexes.by_owner["u1"])
        self.assertIsNotNone(prep.tasks_by_id["t1"].extra)

    def test_build_marks_orphaned_extras(self) -> None:
        store = _FakeExtraStore(extras={"ghost": TaskExtra(task_id="ghost")})
        raw = RawSnapshot(
            source_id="sheet:test",
            source_hash="hash",
            fetched_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"t1": self._sheet("t1", "work", "u1")},
        )

        PrepBuilder(store).build(raw)
        self.assertEqual(store.orphan_calls, ["ghost"])


if __name__ == "__main__":
    unittest.main()

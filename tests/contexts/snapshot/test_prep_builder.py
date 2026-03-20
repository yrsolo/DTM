from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.contexts.snapshot.internal.engine.model import AttachmentMeta, ExtraSnapshot, PrepBuildResult, RawSnapshot, TaskExtra, TaskSheet
from src.contexts.snapshot.internal.engine.prep_builder import PrepBuilder


class _FakeExtraStore:
    def __init__(self, extras: dict[str, TaskExtra] | None = None) -> None:
        self.snapshot = ExtraSnapshot(
            version=2,
            updated_at_utc=datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc),
            items_by_task_id=extras or {},
        )
        self.put_calls = 0

    def get_snapshot(self) -> ExtraSnapshot:
        return self.snapshot

    def put_snapshot(self, snapshot: ExtraSnapshot) -> None:
        self.snapshot = snapshot
        self.put_calls += 1


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
        extra = TaskExtra(
            task_id="t1",
            attachments=[
                AttachmentMeta(
                    id="a1",
                    key="attachments/test/t1/a1-file.pdf",
                    filename="file.pdf",
                    mime="application/pdf",
                    size=10,
                    uploaded_at_utc=datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
                    uploaded_by="tester",
                )
            ],
        )
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

        result: PrepBuildResult = PrepBuilder(store).build(raw)
        prep = result.prep

        self.assertEqual(prep.raw_source_hash, "hash")
        self.assertIn("t1", prep.indexes.by_status["work"])
        self.assertIn("t2", prep.indexes.by_status["done"])
        self.assertIn("t1", prep.indexes.by_owner["u1"])
        self.assertIsNotNone(prep.tasks_by_id["t1"].extra)
        self.assertEqual(prep.tasks_by_id["t1"].extra.attachments[0].filename, "file.pdf")
        for key in ("extra_load_ms", "orphan_reconcile_ms", "task_view_build_ms", "prep_index_build_ms", "prep_build_total_ms"):
            self.assertIn(key, result.timings_ms)
            self.assertGreaterEqual(float(result.timings_ms[key]), 0.0)

    def test_build_marks_orphaned_extras(self) -> None:
        store = _FakeExtraStore(extras={"ghost": TaskExtra(task_id="ghost")})
        raw = RawSnapshot(
            source_id="sheet:test",
            source_hash="hash",
            fetched_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"t1": self._sheet("t1", "work", "u1")},
        )

        result = PrepBuilder(store).build(raw)
        self.assertTrue(result.extra_snapshot_changed)
        self.assertEqual(store.put_calls, 1)
        self.assertTrue(store.snapshot.items_by_task_id["ghost"].orphaned)


if __name__ == "__main__":
    unittest.main()

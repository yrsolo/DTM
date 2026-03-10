from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.snapshot_engine.engine import SnapshotEngine
from src.snapshot_engine.model import AttachmentMeta, ExtraSnapshot, RawSnapshot, TaskExtra, TaskSheet


class _RawCache:
    def __init__(self, raw):
        self._raw = raw

    def get(self):
        return self._raw


class _PrepCache:
    def __init__(self) -> None:
        self.current = None

    def put(self, prep) -> None:  # noqa: ANN001
        self.current = prep


class _ExtraStore:
    def __init__(self) -> None:
        self.snapshot = ExtraSnapshot(version=2, updated_at_utc=datetime.now(timezone.utc), items_by_task_id={})

    def get_snapshot(self) -> ExtraSnapshot:
        return self.snapshot

    def put_snapshot(self, snapshot: ExtraSnapshot) -> None:
        self.snapshot = snapshot


class _PrepBuilder:
    def build(self, raw):  # noqa: ANN001
        from src.snapshot_engine.model import PrepBuildResult, PrepIndexes, PrepSnapshot

        return PrepBuildResult(
            prep=PrepSnapshot(
                source_id=raw.source_id,
                raw_source_hash=raw.source_hash,
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id={},
                indexes=PrepIndexes(),
            )
        )


class SnapshotEngineAttachMetadataTestCase(unittest.TestCase):
    def test_attach_file_metadata_updates_bulk_snapshot(self) -> None:
        raw = RawSnapshot(
            source_id="sheet:test",
            source_hash="hash",
            fetched_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "t1": TaskSheet(
                    task_id="t1",
                    title="Task",
                    owner_id="u1",
                    group_id="g1",
                    brand="b",
                    format_="f",
                    customer="c",
                    raw_timing="",
                    status="work",
                    history="h",
                )
            },
        )
        prep_cache = _PrepCache()
        extra_store = _ExtraStore()
        engine = SnapshotEngine(
            raw_cache=_RawCache(raw),
            prep_cache=prep_cache,
            extra_store=extra_store,
            people_store=None,
            query_engine=None,
            prep_builder=_PrepBuilder(),
            update_job_factory=None,
            people_update_job_factory=None,
        )
        attachment = AttachmentMeta(
            id="a1",
            key="attachments/test/t1/a1.pdf",
            filename="a1.pdf",
            mime="application/pdf",
            size=100,
            uploaded_at_utc=datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc),
            uploaded_by="tester",
        )

        result = engine.attach_file_metadata(task_id="t1", attachment=attachment)

        self.assertEqual(result["status"], "ok")
        self.assertIn("t1", extra_store.snapshot.items_by_task_id)
        self.assertEqual(extra_store.snapshot.items_by_task_id["t1"].attachments[0].filename, "a1.pdf")
        self.assertIsNotNone(prep_cache.current)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.services.errors import TransientError
from src.contexts.snapshot.internal.engine.engine import SnapshotEngine
from src.contexts.snapshot.internal.engine.model import AttachmentMeta, ExtraSnapshot, RawSnapshot, TaskExtra, TaskSheet


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
    def __init__(self, snapshot: ExtraSnapshot) -> None:
        self.snapshot = snapshot
        self.put_calls = 0

    def get_snapshot(self) -> ExtraSnapshot:
        return self.snapshot

    def put_snapshot(self, snapshot: ExtraSnapshot) -> None:
        self.snapshot = snapshot
        self.put_calls += 1


class _PrepBuilder:
    def __init__(self) -> None:
        self.calls = 0

    def build(self, raw):  # noqa: ANN001
        self.calls += 1
        from src.contexts.snapshot.internal.engine.model import PrepBuildResult, PrepIndexes, PrepSnapshot

        return PrepBuildResult(
            prep=PrepSnapshot(
                source_id=raw.source_id,
                raw_source_hash=raw.source_hash,
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id={},
                indexes=PrepIndexes(),
            )
        )


def _attachment(
    *,
    attachment_id: str,
    task_id: str,
    status: str,
    now: datetime,
    storage_key: str | None = None,
) -> AttachmentMeta:
    payload = {
        "attachment_id": attachment_id,
        "task_id": task_id,
        "filename_original": f"{attachment_id}.docx",
        "filename_display": f"{attachment_id}.docx",
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "kind": "docx",
        "size_bytes": 10,
        "storage_bucket": "dtm",
        "storage_key": storage_key or f"attachments/test/{task_id}/{attachment_id}.docx",
        "status": status,
        "uploaded_by_user_id": "tester",
        "uploaded_at_utc": now - timedelta(days=2),
        "verified_at_utc": now - timedelta(days=2),
        "deleted_at_utc": now - timedelta(days=2),
        "snapshot_visible": status == "ready",
        "preview_capabilities": [],
        "sort_key": (now - timedelta(days=2)).isoformat(),
        "preview": "",
    }
    return AttachmentMeta.from_dict(payload)


class SnapshotEngineCleanupAttachmentsTestCase(unittest.TestCase):
    def _engine(self, snapshot: ExtraSnapshot):
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
        prep_builder = _PrepBuilder()
        extra_store = _ExtraStore(snapshot)
        engine = SnapshotEngine(
            attachment_bucket="dtm",
            raw_cache=_RawCache(raw),
            prep_cache=prep_cache,
            extra_store=extra_store,
            people_store=None,
            response_cache_store=None,
            query_engine=None,
            prep_builder=prep_builder,
            update_job_factory=None,
            people_update_job_factory=None,
        )
        return engine, extra_store, prep_builder, prep_cache

    def test_cleanup_removes_stale_pending_uploaded_unverified_and_deleted(self) -> None:
        now = datetime(2026, 3, 15, 12, 0, tzinfo=timezone.utc)
        snapshot = ExtraSnapshot(
            version=2,
            updated_at_utc=now,
            items_by_task_id={
                "t1": TaskExtra(
                    task_id="t1",
                    attachments=[
                        _attachment(attachment_id="p1", task_id="t1", status="pending_upload", now=now),
                        _attachment(attachment_id="u1", task_id="t1", status="uploaded_unverified", now=now),
                        _attachment(attachment_id="d1", task_id="t1", status="deleted", now=now),
                        _attachment(attachment_id="r1", task_id="t1", status="ready", now=now),
                    ],
                )
            },
        )
        deleted_keys = []
        engine, extra_store, prep_builder, prep_cache = self._engine(snapshot)

        result = engine.cleanup_stale_attachments(
            ttl_seconds=86400,
            delete_object=lambda **kwargs: deleted_keys.append(kwargs["key"]),
            now_utc=now,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["pending_removed"], 1)
        self.assertEqual(result["uploaded_unverified_removed"], 1)
        self.assertEqual(result["deleted_removed"], 1)
        self.assertEqual(result["tasks_touched"], 1)
        self.assertTrue(result["prep_written"])
        self.assertEqual(prep_builder.calls, 1)
        self.assertIsNotNone(prep_cache.current)
        self.assertEqual(extra_store.put_calls, 1)
        self.assertEqual([item.attachment_id for item in extra_store.snapshot.items_by_task_id["t1"].attachments], ["r1"])
        self.assertEqual(len(deleted_keys), 3)

    def test_cleanup_keeps_ready_and_invalid_records(self) -> None:
        now = datetime(2026, 3, 15, 12, 0, tzinfo=timezone.utc)
        invalid = AttachmentMeta.from_dict(
            {
                "attachment_id": "",
                "task_id": "",
                "filename_original": "broken.docx",
                "filename_display": "broken.docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "kind": "docx",
                "size_bytes": 10,
                "storage_bucket": "dtm",
                "storage_key": "attachments/test/t1/broken.docx",
                "status": "pending_upload",
                "uploaded_by_user_id": "tester",
                "uploaded_at_utc": now - timedelta(days=3),
                "snapshot_visible": False,
                "preview_capabilities": [],
                "sort_key": (now - timedelta(days=3)).isoformat(),
            }
        )
        snapshot = ExtraSnapshot(
            version=2,
            updated_at_utc=now,
            items_by_task_id={
                "t1": TaskExtra(
                    task_id="t1",
                    attachments=[
                        _attachment(attachment_id="r1", task_id="t1", status="ready", now=now),
                        invalid,
                    ],
                )
            },
        )
        engine, extra_store, prep_builder, prep_cache = self._engine(snapshot)

        result = engine.cleanup_stale_attachments(
            ttl_seconds=86400,
            delete_object=lambda **kwargs: None,
            now_utc=now,
        )

        self.assertEqual(result["pending_removed"], 0)
        self.assertEqual(result["deleted_removed"], 0)
        self.assertFalse(result["prep_written"])
        self.assertEqual(prep_builder.calls, 0)
        self.assertIsNone(prep_cache.current)
        self.assertEqual(extra_store.put_calls, 0)
        self.assertEqual(len(extra_store.snapshot.items_by_task_id["t1"].attachments), 2)

    def test_cleanup_keeps_record_when_storage_delete_is_transient(self) -> None:
        now = datetime(2026, 3, 15, 12, 0, tzinfo=timezone.utc)
        snapshot = ExtraSnapshot(
            version=2,
            updated_at_utc=now,
            items_by_task_id={
                "t1": TaskExtra(
                    task_id="t1",
                    attachments=[_attachment(attachment_id="p1", task_id="t1", status="pending_upload", now=now)],
                )
            },
        )
        engine, extra_store, prep_builder, prep_cache = self._engine(snapshot)

        def _fail(**kwargs):  # noqa: ANN001
            raise TransientError("delete failed", code="attachment_delete_failed")

        result = engine.cleanup_stale_attachments(
            ttl_seconds=86400,
            delete_object=_fail,
            now_utc=now,
        )

        self.assertEqual(result["pending_removed"], 0)
        self.assertIn("t1:p1:attachment_delete_failed", result["warnings"])
        self.assertFalse(result["prep_written"])
        self.assertEqual(prep_builder.calls, 0)
        self.assertIsNone(prep_cache.current)
        self.assertEqual(extra_store.put_calls, 0)
        self.assertEqual(len(extra_store.snapshot.items_by_task_id["t1"].attachments), 1)


if __name__ == "__main__":
    unittest.main()

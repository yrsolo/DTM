from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.snapshot_engine.model import AttachmentMeta, ExtraSnapshot, TaskExtra
from src.snapshot_engine.stores import s3_store


class _DummyError(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class _FakeJsonStore:
    def __init__(self) -> None:
        self.data = {}

    def get(self, key: str):
        return self.data.get(key)

    def put(self, key: str, payload):
        self.data[key] = payload

    def delete(self, key: str):
        self.data.pop(key, None)

    def list_prefix(self, prefix: str):
        return [key for key in self.data if key.startswith(prefix)]


class S3StoreTestCase(unittest.TestCase):
    def test_is_missing_key_codes(self) -> None:
        self.assertTrue(s3_store._is_missing_key(_DummyError("NoSuchKey")))
        self.assertTrue(s3_store._is_missing_key(_DummyError("404")))
        self.assertFalse(s3_store._is_missing_key(_DummyError("AccessDenied")))

    def test_extra_store_uses_bulk_snapshot_key(self) -> None:
        base = _FakeJsonStore()
        store = s3_store.S3ExtraStore(base, "snapshots/extra")
        store.put_snapshot(
            ExtraSnapshot(
                version=2,
                updated_at_utc=datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc),
                items_by_task_id={
                    "t1": TaskExtra(
                        task_id="t1",
                        attachments=[
                            AttachmentMeta(
                                id="a1",
                                key="attachments/test/t1/a1-file.pdf",
                                filename="file.pdf",
                                mime="application/pdf",
                                size=123,
                                uploaded_at_utc=datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
                                uploaded_by="user",
                            )
                        ],
                    )
                },
            )
        )
        self.assertIn("snapshots/extra/default.json", base.data)
        loaded = store.get_snapshot()
        self.assertIn("t1", loaded.items_by_task_id)
        self.assertEqual(len(loaded.items_by_task_id["t1"].attachments), 1)
        self.assertEqual(loaded.items_by_task_id["t1"].attachments[0].filename, "file.pdf")

    def test_extra_store_returns_empty_snapshot_when_missing(self) -> None:
        store = s3_store.S3ExtraStore(_FakeJsonStore(), "snapshots/extra")
        loaded = store.get_snapshot()
        self.assertEqual(loaded.version, 2)
        self.assertEqual(loaded.items_by_task_id, {})

    def test_response_cache_store_roundtrip(self) -> None:
        base = _FakeJsonStore()
        store = s3_store.S3ResponseCacheStore(base, "snapshots/responses")
        store.put("frontend_v2/default/api/full", {"payload": {"ok": True}})
        self.assertIn("snapshots/responses/frontend_v2/default/api/full.json", base.data)
        loaded = store.get("frontend_v2/default/api/full")
        self.assertEqual(loaded, {"payload": {"ok": True}})
        store.delete("frontend_v2/default/api/full")
        self.assertNotIn("snapshots/responses/frontend_v2/default/api/full.json", base.data)


if __name__ == "__main__":
    unittest.main()

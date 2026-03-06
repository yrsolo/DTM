from __future__ import annotations

import unittest

from src.snapshot_engine.model import TaskExtra
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


class S3StoreTestCase(unittest.TestCase):
    def test_is_missing_key_codes(self) -> None:
        self.assertTrue(s3_store._is_missing_key(_DummyError("NoSuchKey")))
        self.assertTrue(s3_store._is_missing_key(_DummyError("404")))
        self.assertFalse(s3_store._is_missing_key(_DummyError("AccessDenied")))

    def test_extra_store_prefix_and_upsert(self) -> None:
        base = _FakeJsonStore()
        store = s3_store.S3ExtraStore(base, "snapshots/extra")
        store.upsert(TaskExtra(task_id="t1"))
        self.assertIn("snapshots/extra/t1.json", base.data)
        loaded = store.get_many(["t1", "t2"])
        self.assertIn("t1", loaded)
        self.assertNotIn("t2", loaded)


if __name__ == "__main__":
    unittest.main()

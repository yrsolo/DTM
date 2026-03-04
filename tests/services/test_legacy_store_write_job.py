from __future__ import annotations

import unittest

from src.entrypoints.jobs.legacy_store_write_job import run_legacy_store_write


class _StoreStub:
    def __init__(self) -> None:
        self.records = []

    def upsert_tasks(self, records):  # noqa: ANN001
        self.records = list(records)
        return {"ok": True, "count": len(self.records)}


class LegacyStoreWriteJobTestCase(unittest.TestCase):
    def test_writes_records_when_enabled(self) -> None:
        store = _StoreStub()
        logs = []
        run_legacy_store_write(
            legacy_blob_write=True,
            store_mode="dual_write",
            mode="timer",
            allow_sync=True,
            tasks=[{"id": "1"}],
            task_to_store_record=lambda task: {"task_id": task["id"]},
            runtime_env="dev",
            ydb_endpoint="ep",
            ydb_database="db",
            migration_store_file="store.json",
            sa_json_credentials=None,
            sa_key_file=None,
            build_store=lambda *args, **kwargs: store,  # noqa: ARG005
            safe_print=logs.append,
        )
        self.assertEqual(len(store.records), 1)
        self.assertTrue(any("migration_store_write=" in line and "records=1" in line for line in logs))

    def test_logs_skip_when_legacy_write_disabled(self) -> None:
        logs = []
        run_legacy_store_write(
            legacy_blob_write=False,
            store_mode="dual_write",
            mode="timer",
            allow_sync=True,
            tasks=[{"id": "1"}],
            task_to_store_record=lambda task: {"task_id": task["id"]},
            runtime_env="dev",
            ydb_endpoint="ep",
            ydb_database="db",
            migration_store_file="store.json",
            sa_json_credentials=None,
            sa_key_file=None,
            build_store=lambda *args, **kwargs: _StoreStub(),  # noqa: ARG005
            safe_print=logs.append,
        )
        self.assertTrue(any("reason=LEGACY_BLOB_WRITE_disabled" in line for line in logs))


if __name__ == "__main__":
    unittest.main()

"""Unit tests for JSON operational store adapter."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from src.platform.infra.operational_store import (
    DualWriteOperationalStore,
    JsonOperationalStore,
    YdbOperationalStore,
    build_operational_store,
)


class JsonOperationalStoreTestCase(unittest.TestCase):
    def test_upsert_is_idempotent_by_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = JsonOperationalStore(Path(tmp_dir) / "store.json")

            first = [
                {"task_id": "t1", "title": "Task A", "status": "work"},
                {"task_id": "t2", "title": "Task B", "status": "work"},
            ]
            store.upsert_tasks(first)

            second = [
                {"task_id": "t1", "title": "Task A changed", "status": "pre_done"},
            ]
            payload = store.upsert_tasks(second)
            tasks = payload["tasks"]

            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks["t1"]["title"], "Task A changed")
            self.assertEqual(tasks["t2"]["title"], "Task B")

    def test_store_factory_falls_back_to_json_without_ydb_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = build_operational_store(
                "dual_write",
                env_name="dev",
                ydb_endpoint="",
                ydb_database="",
                json_file_path=str(Path(tmp_dir) / "store.json"),
            )
            self.assertIsInstance(store, JsonOperationalStore)

    def test_store_factory_selects_ydb_when_settings_present(self) -> None:
        store = build_operational_store(
            "ydb_primary",
            env_name="test",
            ydb_endpoint="grpcs://ydb.serverless.yandexcloud.net:2135/?database=/x/y",
            ydb_database="/x/y",
            json_file_path="artifacts/tmp/ignored.json",
        )
        self.assertIsInstance(store, YdbOperationalStore)

    def test_store_factory_builds_dual_write_when_ydb_present(self) -> None:
        store = build_operational_store(
            "dual_write",
            env_name="test",
            ydb_endpoint="grpcs://ydb.serverless.yandexcloud.net:2135/?database=/x/y",
            ydb_database="/x/y",
            json_file_path="artifacts/tmp/store.json",
        )
        self.assertIsInstance(store, DualWriteOperationalStore)

    def test_store_factory_ydb_only_raises_in_prod_without_config(self) -> None:
        with self.assertRaises(RuntimeError):
            build_operational_store(
                "ydb_only",
                env_name="prod",
                ydb_endpoint="",
                ydb_database="",
                json_file_path="artifacts/tmp/store.json",
            )

    def test_dual_write_keeps_primary_success_on_secondary_error(self) -> None:
        class _Primary:
            def upsert_tasks(self, tasks):
                return {"ok": True, "written": len(tasks)}

            def list_tasks(self):
                return [{"task_id": "a"}]

        class _Secondary:
            def upsert_tasks(self, tasks):
                _ = tasks
                raise RuntimeError("boom")

            def list_tasks(self):
                return []

        store = DualWriteOperationalStore(primary=_Primary(), secondary=_Secondary())
        result = store.upsert_tasks([{"task_id": "a"}])
        self.assertEqual(result.get("backend"), "dual_write")
        self.assertEqual(result.get("primary_result", {}).get("ok"), True)
        self.assertEqual(result.get("secondary_result"), None)
        self.assertIn("boom", str(result.get("secondary_error")))

    def test_ydb_endpoint_normalization_strips_query_params(self) -> None:
        store = YdbOperationalStore(
            endpoint="grpcs://ydb.serverless.yandexcloud.net:2135/?database=/ru-central1/folder/db",
            database="/ru-central1/folder/db",
        )
        self.assertEqual(store.endpoint, "grpcs://ydb.serverless.yandexcloud.net:2135")

    def test_ydb_credentials_prioritize_sa_json(self) -> None:
        fake_ydb = SimpleNamespace(
            iam=SimpleNamespace(
                ServiceAccountCredentials=SimpleNamespace(
                    from_content=mock.Mock(return_value="from_content"),
                    from_file=mock.Mock(return_value="from_file"),
                )
            ),
            credentials_from_env_variables=mock.Mock(return_value="from_env"),
        )
        credentials = YdbOperationalStore._build_credentials(
            fake_ydb,
            sa_json_credentials='{"id":"x"}',
        )
        self.assertEqual(credentials, "from_content")
        fake_ydb.iam.ServiceAccountCredentials.from_content.assert_called_once()
        fake_ydb.credentials_from_env_variables.assert_not_called()


if __name__ == "__main__":
    unittest.main()

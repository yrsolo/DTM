"""Smoke tests for extracted runtime YDB pipeline helper."""

from __future__ import annotations

import importlib
import sys
import types
import unittest


def _import_pipeline_runtime():
    """Import pipeline runtime with lightweight dependency stubs."""

    fake_readmodel_builder = types.ModuleType("src.services.readmodel_builder")

    class _FakeReadmodelBuilderService:  # pragma: no cover - wiring stub
        pass

    fake_readmodel_builder.FrontendReadmodelBuilderService = _FakeReadmodelBuilderService
    sys.modules.setdefault("src.services.readmodel_builder", fake_readmodel_builder)

    fake_sync_service = types.ModuleType("src.services.sync_service")

    class _FakeYdbSyncService:  # pragma: no cover - wiring stub
        pass

    fake_sync_service.YdbSyncService = _FakeYdbSyncService
    sys.modules.setdefault("src.services.sync_service", fake_sync_service)

    module = importlib.import_module("src.services.pipeline_runtime")
    return importlib.reload(module)


class PipelineRuntimeSmokeTestCase(unittest.TestCase):
    def test_pipeline_returns_early_for_legacy_store_mode(self) -> None:
        module = _import_pipeline_runtime()
        flags = {"snapshot_called": False, "payload_called": False}

        def _snapshot(*args, **kwargs):
            flags["snapshot_called"] = True
            return {}

        def _payload(*args, **kwargs):
            flags["payload_called"] = True
            return {}

        module.run_ydb_sync_readmodel_pipeline(
            store_mode="legacy",
            mode="timer",
            allow_sync=True,
            tasks=[],
            source_task_repository=object(),
            force_refresh=False,
            ydb_endpoint="grpcs://example:2135",
            ydb_database="/db",
            ydb_sa_json_credentials=None,
            ydb_sa_key_file=None,
            ydb_migrate_on_start=False,
            write_legacy_milestones=False,
            runtime_env="dev",
            pipeline_cfg=types.SimpleNamespace(
                preflight_top_rows=50,
                readmodel_ttl_minutes=9,
                full_sync_interval_hours=24,
            ),
            safe_print=lambda *_: None,
            read_source_snapshot=_snapshot,
            task_to_operational_payload=_payload,
        )
        self.assertFalse(flags["snapshot_called"])
        self.assertFalse(flags["payload_called"])

    def test_pipeline_returns_early_when_sync_not_allowed(self) -> None:
        module = _import_pipeline_runtime()
        flags = {"snapshot_called": False}

        def _snapshot(*args, **kwargs):
            flags["snapshot_called"] = True
            return {}

        module.run_ydb_sync_readmodel_pipeline(
            store_mode="ydb_primary",
            mode="timer",
            allow_sync=False,
            tasks=[],
            source_task_repository=object(),
            force_refresh=False,
            ydb_endpoint="grpcs://example:2135",
            ydb_database="/db",
            ydb_sa_json_credentials=None,
            ydb_sa_key_file=None,
            ydb_migrate_on_start=False,
            write_legacy_milestones=False,
            runtime_env="dev",
            pipeline_cfg=types.SimpleNamespace(
                preflight_top_rows=50,
                readmodel_ttl_minutes=9,
                full_sync_interval_hours=24,
            ),
            safe_print=lambda *_: None,
            read_source_snapshot=_snapshot,
            task_to_operational_payload=lambda *_: {},
        )
        self.assertFalse(flags["snapshot_called"])


if __name__ == "__main__":
    unittest.main()

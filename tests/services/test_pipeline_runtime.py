"""Smoke tests for extracted runtime YDB pipeline helper."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from types import SimpleNamespace


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

        ctx = module.SyncReadmodelPipelineContext(
            store_mode="legacy",
            allow_sync=True,
            source_task_repository=object(),
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
        request = module.SyncReadmodelPipelineRequest(
            mode="timer",
            tasks=[],
            force_refresh=False,
        )
        module.run_ydb_sync_readmodel_pipeline(ctx, request)
        self.assertFalse(flags["snapshot_called"])
        self.assertFalse(flags["payload_called"])

    def test_pipeline_returns_early_when_sync_not_allowed(self) -> None:
        module = _import_pipeline_runtime()
        flags = {"snapshot_called": False}

        def _snapshot(*args, **kwargs):
            flags["snapshot_called"] = True
            return {}

        ctx = module.SyncReadmodelPipelineContext(
            store_mode="ydb_primary",
            allow_sync=False,
            source_task_repository=object(),
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
        request = module.SyncReadmodelPipelineRequest(
            mode="timer",
            tasks=[],
            force_refresh=False,
        )
        module.run_ydb_sync_readmodel_pipeline(ctx, request)
        self.assertFalse(flags["snapshot_called"])

    def test_pipeline_skips_full_snapshot_fetch_when_preflight_is_unchanged(self) -> None:
        module = _import_pipeline_runtime()
        snapshot_ranges: list[str] = []

        class _FakeOperationalTaskRepo:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

        class _FakeFrontendReadmodelRepo:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

            def get_readmodel(self, readmodel_id):  # noqa: ANN001
                _ = readmodel_id
                return None

        class _FakeSyncService:
            def __init__(self, repo, **kwargs):  # noqa: ANN001, ANN003
                _ = repo, kwargs

            def run_preflight_only(self, **kwargs):  # noqa: ANN003
                _ = kwargs
                return SimpleNamespace(
                    source_id="sheet:test",
                    preflight_hash_50="h50",
                    source_hash_full="hfull",
                    previous_preflight_hash_50="h50_prev",
                    previous_source_hash_full="hfull_prev",
                    no_changes=True,
                    full_sync_performed=False,
                    forced_refresh=False,
                    tasks_upserted=0,
                    milestones_upserted=0,
                    ydb_queries_count=1,
                    ydb_error_code="",
                )

        class _FakeReadmodelBuilder:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

            def run(self, **kwargs):  # noqa: ANN003
                _ = kwargs
                return SimpleNamespace(
                    readmodel_id="frontend_v2:default",
                    source_hash="hash",
                    changed=False,
                    tasks_count=0,
                    ydb_queries_count=1,
                )

        module.OperationalTaskRepo = _FakeOperationalTaskRepo
        module.FrontendReadmodelRepo = _FakeFrontendReadmodelRepo
        module.YdbSyncService = _FakeSyncService
        module.FrontendReadmodelBuilderService = _FakeReadmodelBuilder

        def _snapshot(repo, worksheet_range):  # noqa: ANN001
            _ = repo
            snapshot_ranges.append(str(worksheet_range))
            return {"range": worksheet_range}

        source_task_repository = SimpleNamespace(
            source_sheet_info=SimpleNamespace(
                spreadsheet_name="sheet",
                get_sheet_name=lambda _: "tasks",
            )
        )

        ctx = module.SyncReadmodelPipelineContext(
            store_mode="ydb_primary",
            allow_sync=True,
            source_task_repository=source_task_repository,
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
        request = module.SyncReadmodelPipelineRequest(
            mode="timer",
            tasks=[],
            force_refresh=False,
        )
        module.run_ydb_sync_readmodel_pipeline(ctx, request)
        self.assertEqual(snapshot_ranges, ["A1:Z50"])

    def test_pipeline_fetches_full_snapshot_when_preflight_requires_sync(self) -> None:
        module = _import_pipeline_runtime()
        snapshot_ranges: list[str] = []
        sync_run_called = {"value": False}

        class _FakeOperationalTaskRepo:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

        class _FakeFrontendReadmodelRepo:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

            def get_readmodel(self, readmodel_id):  # noqa: ANN001
                _ = readmodel_id
                return None

        class _FakeSyncService:
            def __init__(self, repo, **kwargs):  # noqa: ANN001, ANN003
                _ = repo, kwargs

            def run_preflight_only(self, **kwargs):  # noqa: ANN003
                _ = kwargs
                return None

            def run(self, **kwargs):  # noqa: ANN003
                _ = kwargs
                sync_run_called["value"] = True
                return SimpleNamespace(
                    source_id="sheet:test",
                    preflight_hash_50="h50",
                    source_hash_full="hfull",
                    previous_preflight_hash_50="h50_prev",
                    previous_source_hash_full="hfull_prev",
                    no_changes=False,
                    full_sync_performed=True,
                    forced_refresh=False,
                    tasks_upserted=1,
                    milestones_upserted=1,
                    ydb_queries_count=1,
                    ydb_error_code="",
                )

        class _FakeReadmodelBuilder:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

            def run(self, **kwargs):  # noqa: ANN003
                _ = kwargs
                return SimpleNamespace(
                    readmodel_id="frontend_v2:default",
                    source_hash="hash",
                    changed=True,
                    tasks_count=1,
                    ydb_queries_count=1,
                )

        module.OperationalTaskRepo = _FakeOperationalTaskRepo
        module.FrontendReadmodelRepo = _FakeFrontendReadmodelRepo
        module.YdbSyncService = _FakeSyncService
        module.FrontendReadmodelBuilderService = _FakeReadmodelBuilder

        def _snapshot(repo, worksheet_range):  # noqa: ANN001
            _ = repo
            snapshot_ranges.append(str(worksheet_range))
            return {"range": worksheet_range}

        source_task_repository = SimpleNamespace(
            source_sheet_info=SimpleNamespace(
                spreadsheet_name="sheet",
                get_sheet_name=lambda _: "tasks",
            )
        )

        ctx = module.SyncReadmodelPipelineContext(
            store_mode="ydb_primary",
            allow_sync=True,
            source_task_repository=source_task_repository,
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
            task_to_operational_payload=lambda task: dict(task),
        )
        request = module.SyncReadmodelPipelineRequest(
            mode="timer",
            tasks=[{"task_id": "1"}],
            force_refresh=False,
        )
        module.run_ydb_sync_readmodel_pipeline(ctx, request)
        self.assertEqual(snapshot_ranges, ["A1:Z50", "A1:Z2000"])
        self.assertTrue(sync_run_called["value"])


if __name__ == "__main__":
    unittest.main()

"""Smoke tests for canonical timer pipeline."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from types import SimpleNamespace

from src.app.context import AppContext


def _import_timer_pipeline():
    """Import timer pipeline with lightweight dependency stubs."""

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

    module = importlib.import_module("src.services.timer_pipeline")
    return importlib.reload(module)


def _cfg(store_mode: str = "ydb_primary") -> SimpleNamespace:
    return SimpleNamespace(
        runtime=SimpleNamespace(
            sources=SimpleNamespace(store_mode_default=store_mode),
            runtime=SimpleNamespace(env_default="dev"),
            pipeline=SimpleNamespace(
                preflight_top_rows=50,
                readmodel_ttl_minutes=9,
                full_sync_interval_hours=24,
            ),
        )
    )


class _FakeMapper:
    def to_operational_payload(self, task):  # noqa: ANN001
        if isinstance(task, dict):
            return dict(task)
        return {"task_id": "1"}


class TimerPipelineSmokeTestCase(unittest.TestCase):
    def test_pipeline_returns_early_for_legacy_store_mode(self) -> None:
        module = _import_timer_pipeline()
        flags = {"snapshot_called": False}

        def _snapshot(*args, **kwargs):
            _ = args, kwargs
            flags["snapshot_called"] = True
            return {}

        task_source = SimpleNamespace(
            source_id="sheet:test:tasks:A1:Z2000",
            source_sheet_name="sheet",
            read_snapshot=_snapshot,
            build_tasks_from_snapshot=lambda *_: [],
        )
        ctx = AppContext(cfg=_cfg(store_mode="legacy"), deps={"task_payload_mapper": _FakeMapper()})
        request = module.RunRequest(mode="timer", force_refresh=False, task_source=task_source)

        module.TimerPipeline(ctx).run(request)
        self.assertFalse(flags["snapshot_called"])

    def test_pipeline_returns_early_for_non_timer_mode(self) -> None:
        module = _import_timer_pipeline()
        flags = {"snapshot_called": False}

        def _snapshot(*args, **kwargs):
            _ = args, kwargs
            flags["snapshot_called"] = True
            return {}

        task_source = SimpleNamespace(
            source_id="sheet:test:tasks:A1:Z2000",
            source_sheet_name="sheet",
            read_snapshot=_snapshot,
            build_tasks_from_snapshot=lambda *_: [],
        )
        ctx = AppContext(cfg=_cfg(), deps={"task_payload_mapper": _FakeMapper()})
        request = module.RunRequest(mode="reminders-only", force_refresh=False, task_source=task_source)

        module.TimerPipeline(ctx).run(request)
        self.assertFalse(flags["snapshot_called"])

    def test_pipeline_executes_for_sync_only_in_legacy_store_mode(self) -> None:
        module = _import_timer_pipeline()
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
                    forced_refresh=True,
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

        def _snapshot(worksheet_range):  # noqa: ANN001
            snapshot_ranges.append(str(worksheet_range))
            return {"range": worksheet_range}

        task_source = SimpleNamespace(
            source_id="sheet:sheet:tasks:A1:Z2000",
            source_sheet_name="sheet",
            read_snapshot=_snapshot,
            build_tasks_from_snapshot=lambda snapshot: [{"task_id": "1"}] if snapshot else [],
        )
        ctx = AppContext(
            cfg=_cfg(store_mode="legacy"),
            deps={
                "task_payload_mapper": _FakeMapper(),
                "ydb_endpoint": "grpcs://example:2135",
                "ydb_database": "/db",
                "ydb_sa_json_credentials": None,
                "ydb_sa_key_file": None,
                "ydb_migrate_on_start": False,
                "write_legacy_milestones": False,
            },
        )
        request = module.RunRequest(mode="sync-only", force_refresh=True, task_source=task_source)

        module.TimerPipeline(ctx).run(request)
        self.assertEqual(snapshot_ranges, ["A1:Z50", "A1:Z2000"])
        self.assertTrue(sync_run_called["value"])

    def test_pipeline_skips_full_snapshot_fetch_when_preflight_is_unchanged(self) -> None:
        module = _import_timer_pipeline()
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

        def _snapshot(worksheet_range):  # noqa: ANN001
            snapshot_ranges.append(str(worksheet_range))
            return {"range": worksheet_range}

        task_source = SimpleNamespace(
            source_id="sheet:sheet:tasks:A1:Z2000",
            source_sheet_name="sheet",
            read_snapshot=_snapshot,
            build_tasks_from_snapshot=lambda *_: [],
        )
        ctx = AppContext(
            cfg=_cfg(),
            deps={
                "task_payload_mapper": _FakeMapper(),
                "ydb_endpoint": "grpcs://example:2135",
                "ydb_database": "/db",
                "ydb_sa_json_credentials": None,
                "ydb_sa_key_file": None,
                "ydb_migrate_on_start": False,
                "write_legacy_milestones": False,
            },
        )
        request = module.RunRequest(mode="timer", force_refresh=False, task_source=task_source)

        module.TimerPipeline(ctx).run(request)
        self.assertEqual(snapshot_ranges, ["A1:Z50"])

    def test_pipeline_fetches_full_snapshot_when_preflight_requires_sync(self) -> None:
        module = _import_timer_pipeline()
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

        def _snapshot(worksheet_range):  # noqa: ANN001
            snapshot_ranges.append(str(worksheet_range))
            return {"range": worksheet_range}

        task_source = SimpleNamespace(
            source_id="sheet:sheet:tasks:A1:Z2000",
            source_sheet_name="sheet",
            read_snapshot=_snapshot,
            build_tasks_from_snapshot=lambda snapshot: [{"task_id": "1"}] if snapshot else [],
        )

        ctx = AppContext(
            cfg=_cfg(),
            deps={
                "task_payload_mapper": _FakeMapper(),
                "ydb_endpoint": "grpcs://example:2135",
                "ydb_database": "/db",
                "ydb_sa_json_credentials": None,
                "ydb_sa_key_file": None,
                "ydb_migrate_on_start": False,
                "write_legacy_milestones": False,
            },
        )
        request = module.RunRequest(mode="timer", force_refresh=False, task_source=task_source)

        module.TimerPipeline(ctx).run(request)
        self.assertEqual(snapshot_ranges, ["A1:Z50", "A1:Z2000"])
        self.assertTrue(sync_run_called["value"])

    def test_pipeline_handles_legacy_int_generated_at_without_crash(self) -> None:
        module = _import_timer_pipeline()
        snapshot_ranges: list[str] = []

        class _FakeOperationalTaskRepo:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

        class _FakeFrontendReadmodelRepo:
            def __init__(self, **kwargs):  # noqa: ANN003
                self.kwargs = kwargs

            def get_readmodel(self, readmodel_id):  # noqa: ANN001
                _ = readmodel_id
                return SimpleNamespace(generated_at_utc=1741123200)

        class _FakeSyncService:
            def __init__(self, repo, **kwargs):  # noqa: ANN001, ANN003
                _ = repo, kwargs

            def run_preflight_only(self, **kwargs):  # noqa: ANN003
                _ = kwargs
                return None

            def run(self, **kwargs):  # noqa: ANN003
                _ = kwargs
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

        def _snapshot(worksheet_range):  # noqa: ANN001
            snapshot_ranges.append(str(worksheet_range))
            return {"range": worksheet_range}

        task_source = SimpleNamespace(
            source_id="sheet:sheet:tasks:A1:Z2000",
            source_sheet_name="sheet",
            read_snapshot=_snapshot,
            build_tasks_from_snapshot=lambda snapshot: [{"task_id": "1"}] if snapshot else [],
        )
        ctx = AppContext(
            cfg=_cfg(),
            deps={
                "task_payload_mapper": _FakeMapper(),
                "ydb_endpoint": "grpcs://example:2135",
                "ydb_database": "/db",
                "ydb_sa_json_credentials": None,
                "ydb_sa_key_file": None,
                "ydb_migrate_on_start": False,
                "write_legacy_milestones": False,
            },
        )
        request = module.RunRequest(mode="timer", force_refresh=False, task_source=task_source)

        result = module.TimerPipeline(ctx).run(request)
        self.assertFalse(result.sync_deferred)
        self.assertIn("A1:Z50", snapshot_ranges)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.info_handler import InfoHandler
from src.observability import StdoutJsonLogger
from src.observability.bottlenecks import RECENT_API_STAGE_EVENTS, RECENT_DIRECT_API_OUTER_TRACES, OuterApiTrace, StageEvent
from src.worker.model import JobStatusRecord


class _FakeSnapshotCache:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


class _FakeSnapshotEngine:
    def __init__(self) -> None:
        now = datetime(2026, 3, 9, 12, 0, tzinfo=timezone.utc)
        prep = SimpleNamespace(
            tasks_by_id={
                "task-1": SimpleNamespace(sheet=SimpleNamespace(status="work")),
                "task-2": SimpleNamespace(sheet=SimpleNamespace(status="done")),
            },
            source_id="sheet:test",
            raw_source_hash="sha256:test",
            built_at_utc=now,
        )
        raw = SimpleNamespace(fetched_at_utc=now)
        self._prep_cache = _FakeSnapshotCache(prep)
        self._raw_cache = _FakeSnapshotCache(raw)


class _FakeStatusStore:
    def __init__(self) -> None:
        self.render_record = JobStatusRecord(
            job_id="job-render-1",
            command_type="render_timeline_sheet",
            status="success",
            requested_at_utc=datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc),
            started_at_utc=datetime(2026, 3, 9, 10, 0, 1, tzinfo=timezone.utc),
            finished_at_utc=datetime(2026, 3, 9, 10, 0, 5, tzinfo=timezone.utc),
            requested_by={"source": "admin"},
            summary={
                "render_applied": False,
                "rows_written": 0,
                "cells_written": 0,
                "target_spreadsheet": "Спонсорские ТНТ ТЕСТ",
                "target_worksheet": "Задачи",
            },
            warnings=["no_matching_tasks"],
        )
        self.update_record = JobStatusRecord(
            job_id="job-update-1",
            command_type="update_snapshot",
            status="failed_terminal",
            requested_at_utc=datetime(2026, 3, 9, 9, 0, tzinfo=timezone.utc),
            finished_at_utc=datetime(2026, 3, 9, 9, 0, 3, tzinfo=timezone.utc),
            requested_by={"source": "trigger"},
            summary={"artifact": "update_snapshot"},
            retryable=False,
            error={"code": "snapshot_failed"},
        )

    def get_recent(self, limit: int = 20):
        return [self.render_record, self.update_record][:limit]

    def get_latest(self, command_type: str):
        if command_type == "render_timeline_sheet":
            return self.render_record
        if command_type == "update_snapshot":
            return self.update_record
        return None


class _MetricsRecorder:
    def __init__(self) -> None:
        self.timings: list[tuple[str, float, dict[str, str]]] = []

    def timing(self, name: str, ms: float, labels=None) -> None:
        self.timings.append((name, float(ms), dict(labels or {})))


class InfoObservabilityTestCase(unittest.TestCase):
    def setUp(self) -> None:
        import src.entrypoints.http.info_handler as module

        self.module = module
        self.original_build_snapshot_engine = module.build_snapshot_engine
        self.original_get_queue_live_stats = module.get_queue_live_stats
        self.original_get_function_build_info = module.get_function_build_info
        self.original_storage_stats = module.InfoHandler._storage_stats
        self._orig_recent_stage_events = list(RECENT_API_STAGE_EVENTS._events)  # type: ignore[attr-defined]
        self._orig_recent_outer_traces = list(RECENT_DIRECT_API_OUTER_TRACES._events)  # type: ignore[attr-defined]
        self.build_snapshot_engine_calls = 0
        self.get_queue_live_stats_calls = 0
        self.get_function_build_info_calls = 0
        self.storage_stats_calls = 0

        def _build_snapshot_engine(_ctx):
            self.build_snapshot_engine_calls += 1
            return _FakeSnapshotEngine()

        def _get_queue_live_stats(**_kwargs):
            self.get_queue_live_stats_calls += 1
            return SimpleNamespace(
                to_dict=lambda: {
                    "queue_name": "dtm-test-commands",
                    "messages_visible": 2,
                    "messages_in_flight": 1,
                    "messages_delayed": 0,
                    "dlq_configured": True,
                }
            )

        def _get_function_build_info(**_kwargs):
            self.get_function_build_info_calls += 1
            return SimpleNamespace(
                function_name="dtm",
                active_version_id="d4etest",
                deployed_at="2026-03-09T09:00:00Z",
                runtime="python311",
                memory="512MB",
                timeout_seconds=240,
                entrypoint="index.handler",
                service_account_id="aje-test",
            )

        def _storage_stats(*_args, **_kwargs):
            self.storage_stats_calls += 1
            return {
                "objectsTotal": 3,
                "bytesTotal": 1024,
                "bytesHuman": "1.00 KB",
                "byPrefix": {"raw": 256, "prep": 256, "extra": 256, "attachments": 256, "jobs": 0},
            }

        module.build_snapshot_engine = _build_snapshot_engine  # type: ignore[assignment]
        module.get_queue_live_stats = _get_queue_live_stats  # type: ignore[assignment]
        module.get_function_build_info = _get_function_build_info  # type: ignore[assignment]
        module.InfoHandler._storage_stats = _storage_stats  # type: ignore[assignment]
        self.metrics = _MetricsRecorder()
        self.ctx = SimpleNamespace(
            cfg=SimpleNamespace(
                runtime=SimpleNamespace(
                    runtime=SimpleNamespace(env_default="test", bottleneck_metrics_level="stages", dev_mode_metrics=True),
                    monitoring=SimpleNamespace(
                        enabled=True,
                        backend="yandex_monitoring",
                        folder_id="folder-test-monitoring",
                        dashboard_name_test="DTM Test Observability",
                        dashboard_name_prod="DTM Prod Observability",
                        dashboard_id_test="dashboard-test-1",
                        dashboard_id_prod="",
                    ),
                    datalens=SimpleNamespace(
                        enabled=True,
                        org_id="org-test",
                        workbook_name="DTM Observability",
                        workbook_id_test="workbook-test-1",
                        workbook_id_prod="",
                        connection_name_test="DTM Monitoring Test",
                        connection_name_prod="",
                        connection_id_test="connection-test-1",
                        connection_id_prod="",
                        dashboard_name_test="DTM Test Ops",
                        dashboard_name_prod="",
                        dashboard_id_test="datalens-dashboard-test-1",
                        dashboard_id_prod="",
                        dashboard_url_test="https://datalens.yandex/org-test/datalens-dashboard-test-1",
                        dashboard_url_prod="",
                    ),
                    prometheus=SimpleNamespace(
                        enabled=True,
                        backend="yandex_managed_prometheus",
                        endpoint_write="https://prometheus-write.test/api/v1/import/prometheus",
                        workspace_id_test="prom-workspace-test-1",
                        workspace_id_prod="",
                    ),
                    grafana=SimpleNamespace(
                        enabled=True,
                        public_base_url="https://dtm.solofarm.ru/grafana",
                        dashboard_uid_test="dtm-test-ops",
                        dashboard_uid_prod="",
                        dashboard_url_test="https://dtm.solofarm.ru/grafana/public-dashboards/test-token",
                        dashboard_url_prod="",
                        embed_url_test="https://dtm.solofarm.ru/grafana/public-dashboards/test-token?kiosk",
                        embed_url_prod="",
                    ),
                    snapshot_engine=SimpleNamespace(
                        bucket="dtm",
                        prefix_raw="snapshots/{env}/raw/default.json",
                        prefix_prep="snapshots/{env}/prep/default.json",
                        prefix_extra="snapshots/{env}/extra/",
                    ),
                    queue=SimpleNamespace(
                        enabled=True,
                        provider="yandex_message_queue",
                        endpoint_url="https://message-queue.api.cloud.yandex.net",
                        test_queue_url="https://message-queue.api.cloud.yandex.net/folder/queue/dtm-test-commands",
                        prod_queue_url="",
                    ),
                    telegram=SimpleNamespace(
                        webhook_path="/telegram",
                        allowed_updates=["message", "callback_query"],
                        max_connections=5,
                        secret_required=True,
                    ),
                    web={"api_domain_test": "dtm.solofarm.ru/test/ops", "api_domain_prod": "dtm.solofarm.ru/ops"},
                ),
                db=SimpleNamespace(object_storage={"endpoint_url_default": "https://storage.yandexcloud.net"}),
                deploy=SimpleNamespace(
                    yandex_cloud=SimpleNamespace(
                        folder_id="folder-test",
                        function_name_test="dtm",
                        function_name_prod="dtm-prod",
                    )
                ),
            ),
            deps={
                "job_status_store": _FakeStatusStore(),
                "tg_webhook_secret_token": "secret",
                "aws_access_key_id": "ak",
                "aws_secret_access_key": "sk",
                "yc_sa_json_credentials": "{}",
                "yc_sa_key_file": "",
                "metrics_client": self.metrics,
                "structured_logger": StdoutJsonLogger(),
            },
        )
        RECENT_API_STAGE_EVENTS._events.clear()  # type: ignore[attr-defined]
        RECENT_API_STAGE_EVENTS.record(
            StageEvent(
                trace_id="trace-1",
                recorded_at="2026-03-09T12:00:00+00:00",
                env="test",
                operation="frontend_access",
                stage="response_cache_read",
                duration_ms=3.5,
                result="success",
                route="api",
                access_mode="masked",
                cache_result="hit",
                debug={},
            )
        )
        RECENT_DIRECT_API_OUTER_TRACES._events.clear()  # type: ignore[attr-defined]
        RECENT_DIRECT_API_OUTER_TRACES.record(
            OuterApiTrace(
                trace_id="outer-trace-1",
                recorded_at="2026-03-09T12:00:10+00:00",
                env="test",
                operation="/api/v2/frontend",
                result="success",
                function_total_ms=1200.0,
                http_shell_total_ms=1100.0,
                router_dispatch_ms=400.0,
                response_build_ms=30.0,
                frontend_handler_ms=200.0,
                frontend_inner_ms=150.0,
                unexplained_in_function_ms=1050.0,
                debug={},
            )
        )

    def tearDown(self) -> None:
        self.module.build_snapshot_engine = self.original_build_snapshot_engine  # type: ignore[assignment]
        self.module.get_queue_live_stats = self.original_get_queue_live_stats  # type: ignore[assignment]
        self.module.get_function_build_info = self.original_get_function_build_info  # type: ignore[assignment]
        self.module.InfoHandler._storage_stats = self.original_storage_stats  # type: ignore[assignment]
        RECENT_API_STAGE_EVENTS._events.clear()  # type: ignore[attr-defined]
        RECENT_API_STAGE_EVENTS._events.extend(self._orig_recent_stage_events)  # type: ignore[attr-defined]
        RECENT_DIRECT_API_OUTER_TRACES._events.clear()  # type: ignore[attr-defined]
        RECENT_DIRECT_API_OUTER_TRACES._events.extend(self._orig_recent_outer_traces)  # type: ignore[attr-defined]

    def test_info_json_default_summary_skips_heavy_diagnostics(self) -> None:
        handler = InfoHandler(self.ctx)
        response = handler.handle(
            HttpRequest(method="GET", path="/info", query={"format": "json"}, is_http_event=True)
        )
        self.assertIsNotNone(response)
        payload = json.loads(response.body)
        self.assertEqual(payload["view"], "summary")
        self.assertTrue(payload["counts"]["detailDeferred"])
        self.assertTrue(payload["storage"]["detailDeferred"])
        self.assertTrue(payload["jobs"]["detailDeferred"])
        self.assertTrue(payload["build"]["detailDeferred"])
        self.assertEqual(payload["bottlenecks"]["profilingLevel"], "stages")
        self.assertTrue(payload["bottlenecks"]["recentApiTracesDeferred"])
        self.assertTrue(payload["bottlenecks"]["recentDirectApiOuterTracesDeferred"])
        self.assertEqual(self.build_snapshot_engine_calls, 0)
        self.assertEqual(self.get_queue_live_stats_calls, 0)
        self.assertEqual(self.get_function_build_info_calls, 0)
        self.assertEqual(self.storage_stats_calls, 0)
        timing_names = [item[0] for item in self.metrics.timings]
        self.assertIn("dtm.info.summary.ms", timing_names)
        self.assertNotIn("dtm.info.detail.ms", timing_names)

    def test_info_json_detail_includes_build_queue_jobs_and_render_debug(self) -> None:
        handler = InfoHandler(self.ctx)
        response = handler.handle(
            HttpRequest(
                method="GET",
                path="/info",
                query={"format": "json", "view": "detail"},
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        payload = json.loads(response.body)
        self.assertEqual(payload["view"], "detail")
        self.assertIn("build", payload)
        self.assertIn("queue", payload)
        self.assertIn("live", payload["queue"])
        self.assertIn("jobs", payload)
        self.assertIn("telemetry", payload)
        self.assertEqual(payload["renderDebug"]["state"], "noop")
        self.assertEqual(payload["build"]["activeVersionId"], "d4etest")
        self.assertEqual(payload["queue"]["live"]["messages_visible"], 2)
        self.assertEqual(payload["queue"]["policy"]["retryModel"], "queue_driven")
        self.assertEqual(payload["telemetry"]["metricsClient"], "_MetricsRecorder")
        self.assertEqual(payload["telemetry"]["bottleneckMetricsLevel"], "stages")
        self.assertTrue(payload["telemetry"]["monitoringEnabled"])
        self.assertEqual(payload["telemetry"]["monitoringBackend"], "yandex_monitoring")
        self.assertEqual(payload["telemetry"]["dashboardName"], "DTM Test Observability")
        self.assertEqual(payload["telemetry"]["dashboardId"], "dashboard-test-1")
        self.assertTrue(payload["telemetry"]["datalensEnabled"])
        self.assertEqual(payload["telemetry"]["datalensOrgId"], "org-test")
        self.assertEqual(payload["telemetry"]["datalensWorkbookId"], "workbook-test-1")
        self.assertEqual(payload["telemetry"]["datalensConnectionId"], "connection-test-1")
        self.assertEqual(payload["telemetry"]["datalensDashboardId"], "datalens-dashboard-test-1")
        self.assertTrue(payload["telemetry"]["prometheusEnabled"])
        self.assertEqual(payload["telemetry"]["prometheusBackend"], "yandex_managed_prometheus")
        self.assertEqual(payload["telemetry"]["prometheusWorkspaceId"], "prom-workspace-test-1")
        self.assertTrue(payload["telemetry"]["grafanaEnabled"])
        self.assertEqual(payload["telemetry"]["grafanaDashboardUid"], "dtm-test-ops")
        self.assertEqual(
            payload["telemetry"]["grafanaDashboardUrl"],
            "https://dtm.solofarm.ru/grafana/public-dashboards/test-token",
        )
        self.assertTrue(payload["bottlenecks"]["stageMetricsEnabled"])
        self.assertEqual(payload["bottlenecks"]["recentApiTraces"][0]["traceId"], "trace-1")
        self.assertEqual(payload["bottlenecks"]["recentDirectApiOuterTraces"][0]["traceId"], "outer-trace-1")
        self.assertEqual(len(payload["jobs"]["recent"]), 2)
        self.assertGreater(self.build_snapshot_engine_calls, 0)
        self.assertGreater(self.get_queue_live_stats_calls, 0)
        self.assertGreater(self.get_function_build_info_calls, 0)
        self.assertGreater(self.storage_stats_calls, 0)
        timing_names = [item[0] for item in self.metrics.timings]
        self.assertIn("dtm.info.summary.ms", timing_names)
        self.assertIn("dtm.info.detail.ms", timing_names)

    def test_info_html_contains_new_operational_sections(self) -> None:
        handler = InfoHandler(self.ctx)
        response = handler.handle(HttpRequest(method="GET", path="/info", is_http_event=True))
        self.assertIsNotNone(response)
        self.assertIn("Function Build", response.body)
        self.assertIn("Queue State", response.body)
        self.assertIn("Recent Jobs", response.body)
        self.assertIn("Last Render Job", response.body)
        self.assertIn("/info?format=json&view=detail", response.body)
        self.assertIn("access mode:", response.body)
        self.assertIn("full (with cookie)", response.body)
        self.assertIn("masked (omit cookie)", response.body)
        self.assertIn("target route:", response.body)
        self.assertIn("browser proxy (/bff/api)", response.body)
        self.assertIn("direct backend (/api)", response.body)
        self.assertIn("Bottleneck Profiling", response.body)
        self.assertIn("Bottleneck Diagnostics", response.body)

    def test_info_json_includes_ui_base_path_for_prefixed_route(self) -> None:
        handler = InfoHandler(self.ctx)
        response = handler.handle(
            HttpRequest(
                method="GET",
                path="/info",
                query={"format": "json"},
                raw_event={"url": "https://dtm.solofarm.ru/test/ops/info?format=json"},
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        payload = json.loads(response.body)
        self.assertEqual(payload.get("web", {}).get("uiBasePath"), "/test/ops")


if __name__ == "__main__":
    unittest.main()

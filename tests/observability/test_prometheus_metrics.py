from __future__ import annotations

import unittest
from unittest.mock import patch

from src.infra.yc_prometheus import (
    build_prometheus_metric_sample,
    build_remote_write_payload,
    normalize_prometheus_labels,
    normalize_prometheus_metric_name,
    workspace_query_endpoint,
    workspace_remote_write_endpoint,
)
from src.observability.composite_metrics import CompositeMetricsClient
from src.observability.metrics import NoopMetricsClient
from src.observability.prometheus_metrics import YandexManagedPrometheusRemoteWriteClient


class _RecordingLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def warning(self, event: str, **fields: object) -> None:
        self.events.append((event, dict(fields)))


class _RecordingMetrics(NoopMetricsClient):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, float]] = []

    def counter(self, name: str, value: int = 1, labels=None) -> None:
        self.calls.append(("counter", name, float(value)))


class PrometheusMetricsClientTestCase(unittest.TestCase):
    def test_normalize_metric_name_uses_underscores(self) -> None:
        self.assertEqual(
            normalize_prometheus_metric_name("dtm.snapshot.update_duration_ms"),
            "dtm_snapshot_update_duration_ms",
        )

    def test_normalize_labels_drops_empty_values(self) -> None:
        labels = normalize_prometheus_labels({"env": "test", "module": "", " ": "x"})
        self.assertEqual(labels, {"env": "test"})

    def test_build_prometheus_metric_sample_adds_service_and_namespace(self) -> None:
        sample = build_prometheus_metric_sample(
            name="dtm.render.write_sheet_ms",
            value=12.0,
            labels={"env": "test"},
            service_label="dtm",
            namespace="dtm",
            ts_ms=123,
        )
        self.assertEqual(sample.name, "dtm_render_write_sheet_ms")
        self.assertEqual(sample.labels["service"], "dtm")
        self.assertEqual(sample.labels["namespace"], "dtm")
        self.assertEqual(sample.ts_ms, 123)

    def test_build_remote_write_payload_contains_metric_name_and_labels(self) -> None:
        sample = build_prometheus_metric_sample(
            name="dtm.api.requests_total",
            value=1.0,
            labels={"env": "test", "operation": "frontend"},
            service_label="dtm",
            namespace="dtm",
            ts_ms=456,
        )
        payload = build_remote_write_payload([sample])
        self.assertIsInstance(payload, bytes)
        self.assertTrue(payload)
        self.assertIn(b"dtm_api_requests_total", payload)
        self.assertIn(b"__name__", payload)
        self.assertIn(b"frontend", payload)

    def test_workspace_remote_write_endpoint_uses_workspace_id(self) -> None:
        self.assertEqual(
            workspace_remote_write_endpoint("workspace-test"),
            "https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/write",
        )

    def test_workspace_query_endpoint_uses_workspace_id(self) -> None:
        self.assertEqual(
            workspace_query_endpoint("workspace-test"),
            "https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/query",
        )

    def test_prometheus_client_writes_remote_write_payload(self) -> None:
        logger = _RecordingLogger()
        calls: list[dict[str, object]] = []

        def _fake_write(**kwargs):
            calls.append(dict(kwargs))
            return {"status": "ok"}

        with patch("src.observability.prometheus_metrics.write_prometheus_remote_write", side_effect=_fake_write):
            client = YandexManagedPrometheusRemoteWriteClient(
                endpoint_write="https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/write",
                api_key="api-key-test",
                logger=logger,
                service_label="dtm",
                namespace="dtm",
            )
            client.timing(
                "dtm.snapshot.fetch_sheet_ms",
                10.5,
                {"env": "test", "module": "snapshot", "operation": "update", "result": "success"},
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0]["endpoint_write"],
            "https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/write",
        )
        self.assertEqual(calls[0]["bearer_token"], "api-key-test")
        sample = calls[0]["metrics"][0]
        self.assertEqual(sample.name, "dtm_snapshot_fetch_sheet_ms")
        self.assertEqual(sample.labels["env"], "test")
        self.assertEqual(logger.events, [])

    def test_prometheus_client_swallow_write_failure(self) -> None:
        logger = _RecordingLogger()
        with patch(
            "src.observability.prometheus_metrics.write_prometheus_remote_write",
            side_effect=RuntimeError("boom"),
        ):
            client = YandexManagedPrometheusRemoteWriteClient(
                endpoint_write="https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/write",
                api_key="api-key-test",
                logger=logger,
                service_label="dtm",
                namespace="dtm",
            )
            client.counter("dtm.api.requests_total", labels={"env": "test"})
        self.assertEqual(len(logger.events), 1)
        event, fields = logger.events[0]
        self.assertEqual(event, "prometheus_metric_emit_failed")
        self.assertEqual(fields["metric"], "dtm.api.requests_total")

    def test_composite_metrics_client_fans_out(self) -> None:
        first = _RecordingMetrics()
        second = _RecordingMetrics()
        client = CompositeMetricsClient([first, second])
        client.counter("dtm.test.counter", 2)
        self.assertEqual(len(first.calls), 1)
        self.assertEqual(len(second.calls), 1)


if __name__ == "__main__":
    unittest.main()

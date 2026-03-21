from __future__ import annotations

import unittest
from unittest.mock import patch

from src.platform.integrations.yandex_cloud.monitoring import build_metric_point, normalize_metric_labels
from src.platform.observability.metrics import MetricEntry, YandexMonitoringMetricsClient


class _RecordingLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def warning(self, event: str, **fields: object) -> None:
        self.events.append((event, dict(fields)))


class YandexMonitoringMetricsClientTestCase(unittest.TestCase):
    def test_normalize_metric_labels_drops_empty_values(self) -> None:
        labels = normalize_metric_labels({"env": "test", "module": "", "operation": "api", " ": "x"})
        self.assertEqual(labels, {"env": "test", "operation": "api"})

    def test_build_metric_point_adds_service_and_namespace_labels(self) -> None:
        point = build_metric_point(
            name="dtm.api.requests_total",
            value=1.0,
            labels={"env": "test"},
            service_label="dtm",
            namespace="dtm",
        )
        self.assertEqual(point.labels["env"], "test")
        self.assertEqual(point.labels["service_name"], "dtm")
        self.assertEqual(point.labels["namespace"], "dtm")
        self.assertTrue(point.ts)

    def test_client_writes_metric_using_monitoring_adapter(self) -> None:
        logger = _RecordingLogger()
        calls: list[tuple[str, str, str, list[object]]] = []

        def _fake_write_metrics(**kwargs):
            calls.append(
                (
                    str(kwargs["endpoint_write"]),
                    str(kwargs["folder_id"]),
                    str(kwargs["iam_token"]),
                    list(kwargs["metrics"]),
                )
            )
            return {"writtenMetricsCount": 1}

        with patch("src.platform.observability.metrics.write_metrics", side_effect=_fake_write_metrics):
            client = YandexMonitoringMetricsClient(
                folder_id="folder-1",
                iam_token_provider=lambda: "iam-test",
                logger=logger,
                endpoint_write="https://monitoring.api.cloud.yandex.net/monitoring/v2/data/write",
                service_label="dtm",
                namespace="dtm",
            )
            client.counter("dtm.api.requests_total", labels={"env": "test", "module": "api", "operation": "frontend", "result": "success"})

        self.assertEqual(len(calls), 1)
        endpoint_write, folder_id, iam_token, metrics = calls[0]
        self.assertIn("/monitoring/v2/data/write", endpoint_write)
        self.assertEqual(folder_id, "folder-1")
        self.assertEqual(iam_token, "iam-test")
        self.assertEqual(metrics[0].name, "dtm.api.requests_total")
        self.assertEqual(metrics[0].labels["env"], "test")
        self.assertEqual(logger.events, [])

    def test_client_swallow_write_failure_and_logs_warning(self) -> None:
        logger = _RecordingLogger()
        with patch("src.platform.observability.metrics.write_metrics", side_effect=RuntimeError("boom")):
            client = YandexMonitoringMetricsClient(
                folder_id="folder-1",
                iam_token_provider=lambda: "iam-test",
                logger=logger,
                endpoint_write="https://monitoring.api.cloud.yandex.net/monitoring/v2/data/write",
                service_label="dtm",
                namespace="dtm",
            )
            client.gauge("dtm.render.cells_written", 123.0, {"env": "test"})

        self.assertEqual(len(logger.events), 1)
        event, fields = logger.events[0]
        self.assertEqual(event, "monitoring_metric_flush_failed")
        self.assertEqual(fields["metric_count"], 1)

    def test_client_flush_entries_writes_one_batch_for_many_points(self) -> None:
        logger = _RecordingLogger()
        calls: list[list[object]] = []

        def _fake_write_metrics(**kwargs):
            calls.append(list(kwargs["metrics"]))
            return {"writtenMetricsCount": len(kwargs["metrics"])}

        with patch("src.platform.observability.metrics.write_metrics", side_effect=_fake_write_metrics):
            client = YandexMonitoringMetricsClient(
                folder_id="folder-1",
                iam_token_provider=lambda: "iam-test",
                logger=logger,
                endpoint_write="https://monitoring.api.cloud.yandex.net/monitoring/v2/data/write",
                service_label="dtm",
                namespace="dtm",
            )
            results = client.flush_entries(
                [
                    MetricEntry(kind="metric", name="dtm.api.requests_total", value=1.0, labels={"env": "test"}),
                    MetricEntry(kind="metric", name="dtm.api.duration_ms", value=12.0, labels={"env": "test"}),
                ]
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0]), 2)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].backend, "monitoring")
        self.assertEqual(results[0].points_total, 2)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.platform.observability.batching import (
    FlushReport,
    MetricsBatchCollector,
    add_flush_metrics,
    is_debug_metrics_enabled,
    is_detailed_metrics_enabled,
    is_stage_metrics_enabled,
    resolve_bottleneck_metrics_level,
)
from src.platform.observability.buffered_metrics import BufferedMetricsClient, managed_metrics_scope
from src.platform.observability.metrics import BackendFlushResult, MetricEntry, NoopMetricsClient


class _BatchRecordingMetrics(NoopMetricsClient):
    def __init__(self) -> None:
        self.flushed: list[list[MetricEntry]] = []

    def flush_entries(self, entries):
        batch = list(entries)
        self.flushed.append(batch)
        return [BackendFlushResult(backend="monitoring", duration_ms=12.5, points_total=len(batch))]


class MetricsBatchingTestCase(unittest.TestCase):
    def test_collector_accumulates_entries_and_flushes_once(self) -> None:
        metrics = _BatchRecordingMetrics()
        collector = MetricsBatchCollector(metrics)
        collector.counter("dtm.test.counter", 2, {"env": "test"})
        collector.gauge("dtm.test.gauge", 3.5, {"env": "test"})
        collector.timing("dtm.test.duration_ms", 7.0, {"env": "test"})

        report = collector.flush()

        self.assertEqual(len(metrics.flushed), 1)
        self.assertEqual(len(metrics.flushed[0]), 3)
        self.assertEqual(report.total_points, 3)
        self.assertGreater(report.total_duration_ms, 0.0)

    def test_add_flush_metrics_adds_backend_and_combined_points(self) -> None:
        metrics = _BatchRecordingMetrics()
        collector = MetricsBatchCollector(metrics)
        report = FlushReport(
            backend_results=[
                BackendFlushResult(backend="monitoring", duration_ms=12.0, points_total=8, failed=False),
                BackendFlushResult(backend="prometheus", duration_ms=20.0, points_total=8, failed=True, error="boom"),
            ]
        )

        add_flush_metrics(
            collector,
            env_name="test",
            module="snapshot",
            operation="update",
            report=report,
        )
        collector.flush()

        names = [entry.name for entry in metrics.flushed[0]]
        self.assertIn("dtm.metrics.flush_duration_ms", names)
        self.assertIn("dtm.metrics.flush_points_total", names)
        self.assertIn("dtm.metrics.flush_failures_total", names)
        combined = [entry for entry in metrics.flushed[0] if (entry.labels or {}).get("backend") == "combined"]
        self.assertTrue(combined)

    def test_bottleneck_metrics_level_reads_explicit_policy(self) -> None:
        ctx = SimpleNamespace(
            cfg=SimpleNamespace(
                runtime=SimpleNamespace(runtime=SimpleNamespace(bottleneck_metrics_level="debug", dev_mode_metrics=False))
            )
        )
        self.assertEqual(resolve_bottleneck_metrics_level(ctx), "debug")
        self.assertTrue(is_stage_metrics_enabled(ctx))
        self.assertTrue(is_debug_metrics_enabled(ctx))

    def test_bottleneck_metrics_level_uses_dev_mode_backward_compat(self) -> None:
        ctx = SimpleNamespace(
            cfg=SimpleNamespace(
                runtime=SimpleNamespace(runtime=SimpleNamespace(bottleneck_metrics_level="", dev_mode_metrics=True))
            )
        )
        self.assertEqual(resolve_bottleneck_metrics_level(ctx), "stages")
        self.assertTrue(is_detailed_metrics_enabled(ctx))
        self.assertFalse(is_debug_metrics_enabled(ctx))

    def test_bottleneck_metrics_level_defaults_to_off(self) -> None:
        ctx = SimpleNamespace(
            cfg=SimpleNamespace(
                runtime=SimpleNamespace(runtime=SimpleNamespace(bottleneck_metrics_level="off", dev_mode_metrics=False))
            )
        )
        self.assertEqual(resolve_bottleneck_metrics_level(ctx), "off")
        self.assertFalse(is_stage_metrics_enabled(ctx))

    def test_buffered_client_accumulates_until_scope_end(self) -> None:
        sink = _BatchRecordingMetrics()
        metrics = BufferedMetricsClient(sink)
        with managed_metrics_scope(metrics):
            metrics.counter("dtm.test.counter", 2, {"env": "test"})
            metrics.gauge("dtm.test.gauge", 3.5, {"env": "test"})
            metrics.timing("dtm.test.duration_ms", 7.0, {"env": "test"})
            self.assertEqual(sink.flushed, [])
        self.assertEqual(len(sink.flushed), 1)
        self.assertEqual(len(sink.flushed[0]), 3)

    def test_buffered_collector_flush_does_not_hit_sink_until_scope_end(self) -> None:
        sink = _BatchRecordingMetrics()
        metrics = BufferedMetricsClient(sink)
        collector = MetricsBatchCollector(metrics)
        with managed_metrics_scope(metrics):
            collector.counter("dtm.test.counter", 1, {"env": "test"})
            report = collector.flush()
            self.assertEqual(report.total_points, 0)
            self.assertEqual(sink.flushed, [])
        self.assertEqual(len(sink.flushed), 1)
        self.assertEqual(len(sink.flushed[0]), 1)


if __name__ == "__main__":
    unittest.main()

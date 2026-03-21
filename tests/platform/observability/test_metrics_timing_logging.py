from __future__ import annotations

import json
import unittest

from src.platform.observability.logging import StdoutJsonLogger
from src.platform.observability.metrics import NoopMetricsClient
from src.platform.observability.timing import timed


class _RecordingMetrics(NoopMetricsClient):
    def __init__(self) -> None:
        self.timings: list[tuple[str, float, dict[str, str]]] = []

    def timing(self, name: str, ms: float, labels=None) -> None:
        self.timings.append((name, ms, dict(labels or {})))


class ObservabilityHelpersTestCase(unittest.TestCase):
    def test_noop_metrics_client_is_callable(self) -> None:
        client = NoopMetricsClient()
        client.counter("dtm.test.counter")
        client.gauge("dtm.test.gauge", 1.0)
        client.timing("dtm.test.timing", 2.0)

    def test_timed_context_emits_timing_on_exit(self) -> None:
        metrics = _RecordingMetrics()
        with timed(metrics, "dtm.test.duration_ms", {"module": "test"}):
            pass

        self.assertEqual(len(metrics.timings), 1)
        name, elapsed_ms, labels = metrics.timings[0]
        self.assertEqual(name, "dtm.test.duration_ms")
        self.assertGreaterEqual(elapsed_ms, 0.0)
        self.assertEqual(labels["module"], "test")

    def test_stdout_json_logger_formats_json_events(self) -> None:
        logger = StdoutJsonLogger()
        payload = logger._serialize("test_event", level="info", alpha=1)  # type: ignore[attr-defined]
        parsed = json.loads(payload)
        self.assertEqual(parsed["event"], "test_event")
        self.assertEqual(parsed["level"], "info")
        self.assertEqual(parsed["alpha"], 1)


if __name__ == "__main__":
    unittest.main()

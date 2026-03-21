from __future__ import annotations

import time
from contextlib import contextmanager


@contextmanager
def timed(metrics, metric_name: str, labels: dict[str, str] | None = None):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        if metrics is not None:
            metrics.timing(metric_name, elapsed_ms, labels or {})

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.observability.metrics import BackendFlushResult, MetricEntry, MetricsClient


@dataclass(frozen=True, slots=True)
class FlushReport:
    backend_results: list[BackendFlushResult] = field(default_factory=list)

    @property
    def total_duration_ms(self) -> float:
        return float(sum(result.duration_ms for result in self.backend_results))

    @property
    def total_points(self) -> int:
        return int(sum(result.points_total for result in self.backend_results))


class MetricsBatchCollector:
    def __init__(self, metrics: MetricsClient | None) -> None:
        self._metrics = metrics
        self._entries: list[MetricEntry] = []

    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        self._entries.append(MetricEntry(kind="counter", name=name, value=float(value), labels=labels))

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._entries.append(MetricEntry(kind="gauge", name=name, value=float(value), labels=labels))

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        self._entries.append(MetricEntry(kind="timing", name=name, value=float(ms), labels=labels))

    def flush(self) -> FlushReport:
        if self._metrics is None or not self._entries:
            return FlushReport([])
        backend_results = list(self._metrics.flush_entries(list(self._entries)))
        self._entries.clear()
        return FlushReport(backend_results)


def add_flush_metrics(
    collector: MetricsBatchCollector,
    *,
    env_name: str,
    module: str,
    operation: str,
    report: FlushReport,
) -> None:
    base = {
        "env": str(env_name or "").strip() or "unknown",
        "module": str(module or "").strip() or "unknown",
        "operation": str(operation or "").strip() or "unknown",
    }
    for result in report.backend_results:
        backend_labels = {
            **base,
            "backend": result.backend,
            "result": "failed" if result.failed else "success",
        }
        collector.timing(
            "dtm.metrics.flush_duration_ms",
            float(result.duration_ms),
            backend_labels,
        )
        collector.counter(
            "dtm.metrics.flush_points_total",
            int(result.points_total),
            backend_labels,
        )
        if result.failed:
            collector.counter(
                "dtm.metrics.flush_failures_total",
                1,
                backend_labels,
            )
    combined_result = "failed" if any(result.failed for result in report.backend_results) else "success"
    combined_labels = {**base, "backend": "combined", "result": combined_result}
    collector.timing(
        "dtm.metrics.flush_duration_ms",
        float(report.total_duration_ms),
        combined_labels,
    )
    collector.counter(
        "dtm.metrics.flush_points_total",
        int(report.total_points),
        combined_labels,
    )
    if combined_result == "failed":
        collector.counter(
            "dtm.metrics.flush_failures_total",
            1,
            combined_labels,
        )


def emit_flush_metrics(
    metrics: MetricsClient | None,
    *,
    env_name: str,
    module: str,
    operation: str,
    report: FlushReport,
) -> None:
    if metrics is None:
        return
    collector = MetricsBatchCollector(metrics)
    add_flush_metrics(
        collector,
        env_name=env_name,
        module=module,
        operation=operation,
        report=report,
    )
    collector.flush()


def is_detailed_metrics_enabled(ctx: Any) -> bool:
    try:
        return bool(ctx.cfg.runtime.runtime.dev_mode_metrics)
    except Exception:
        return False

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Iterator

from src.observability.metrics import BackendFlushResult, MetricEntry, MetricsClient, NoopMetricsClient


@dataclass(slots=True)
class _BufferedScopeState:
    entries: list[MetricEntry] = field(default_factory=list)


class BufferedMetricsClient(MetricsClient):
    def __init__(self, sink: MetricsClient | None) -> None:
        self._sink = sink if sink is not None else NoopMetricsClient()
        self._scope_var: ContextVar[_BufferedScopeState | None] = ContextVar(
            "buffered_metrics_scope",
            default=None,
        )

    @property
    def sink(self) -> MetricsClient:
        return self._sink

    def has_active_scope(self) -> bool:
        return self._scope_var.get() is not None

    @contextmanager
    def buffered_scope(self) -> Iterator[None]:
        current = self._scope_var.get()
        if current is not None:
            yield
            return
        token = self._scope_var.set(_BufferedScopeState())
        try:
            yield
        finally:
            self._scope_var.reset(token)

    def flush_buffer(self) -> list[BackendFlushResult]:
        state = self._scope_var.get()
        if state is None or not state.entries:
            return []
        batch = list(state.entries)
        state.entries.clear()
        return list(self._sink.flush_entries(batch))

    def _emit_entry(self, entry: MetricEntry) -> None:
        state = self._scope_var.get()
        if state is not None:
            state.entries.append(entry)
            return
        self._sink.flush_entries([entry])

    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        self._emit_entry(MetricEntry(kind="counter", name=name, value=float(value), labels=labels))

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._emit_entry(MetricEntry(kind="gauge", name=name, value=float(value), labels=labels))

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        self._emit_entry(MetricEntry(kind="timing", name=name, value=float(ms), labels=labels))

    def flush_entries(self, entries: list[MetricEntry]) -> list[BackendFlushResult]:
        batch = [entry for entry in list(entries or []) if str(entry.name or "").strip()]
        if not batch:
            return []
        state = self._scope_var.get()
        if state is not None:
            state.entries.extend(batch)
            return []
        return list(self._sink.flush_entries(batch))


def metrics_sink_name(metrics: MetricsClient | None) -> str:
    if isinstance(metrics, BufferedMetricsClient):
        return type(metrics.sink).__name__
    if metrics is None:
        return "None"
    return type(metrics).__name__


def remote_metrics_enabled(metrics: MetricsClient | None) -> bool:
    sink = metrics.sink if isinstance(metrics, BufferedMetricsClient) else metrics
    return sink is not None and not isinstance(sink, NoopMetricsClient)


@contextmanager
def managed_metrics_scope(metrics: MetricsClient | None) -> Iterator[None]:
    if not isinstance(metrics, BufferedMetricsClient):
        yield
        return
    with metrics.buffered_scope():
        try:
            yield
        finally:
            try:
                metrics.flush_buffer()
            except Exception:
                # Metrics delivery is best-effort and must not break request/job flow.
                pass

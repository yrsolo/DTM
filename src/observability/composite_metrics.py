from __future__ import annotations

from src.observability.metrics import BackendFlushResult, MetricEntry, MetricsClient


class CompositeMetricsClient(MetricsClient):
    def __init__(self, clients: list[MetricsClient]) -> None:
        self._clients = [client for client in list(clients or []) if client is not None]

    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        for client in self._clients:
            client.counter(name, value, labels)

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        for client in self._clients:
            client.gauge(name, value, labels)

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        for client in self._clients:
            client.timing(name, ms, labels)

    def flush_entries(self, entries: list[MetricEntry]) -> list[BackendFlushResult]:
        backend_results: list[BackendFlushResult] = []
        for client in self._clients:
            backend_results.extend(client.flush_entries(list(entries)))
        return backend_results

from __future__ import annotations

from time import perf_counter
from typing import Any

from src.platform.integrations.yandex_cloud.prometheus import (
    build_prometheus_metric_sample,
    write_prometheus_remote_write,
)
from src.platform.observability.metrics import BackendFlushResult, MetricEntry, MetricsClient


class YandexManagedPrometheusRemoteWriteClient(MetricsClient):
    """Best-effort Yandex Managed Prometheus remote-write backend."""

    def __init__(
        self,
        endpoint_write: str,
        api_key: str,
        logger: Any,
        *,
        service_label: str,
        namespace: str,
        timeout_seconds: float = 2.0,
    ) -> None:
        self._endpoint_write = str(endpoint_write or "").strip()
        self._api_key = str(api_key or "").strip()
        self._logger = logger
        self._service_label = str(service_label or "").strip() or "dtm"
        self._namespace = str(namespace or "").strip() or "dtm"
        self._timeout_seconds = max(0.1, float(timeout_seconds))

    def flush_entries(self, entries: list[MetricEntry]) -> list[BackendFlushResult]:
        batch = [entry for entry in list(entries or []) if str(entry.name or "").strip()]
        if not batch or not self._endpoint_write or not self._api_key:
            return []
        started_at = perf_counter()
        try:
            samples = [
                build_prometheus_metric_sample(
                    name=str(entry.name).strip(),
                    value=float(entry.value),
                    labels=entry.labels,
                    service_label=self._service_label,
                    namespace=self._namespace,
                )
                for entry in batch
            ]
            write_prometheus_remote_write(
                endpoint_write=self._endpoint_write,
                metrics=samples,
                bearer_token=self._api_key,
                timeout_seconds=self._timeout_seconds,
            )
            return [
                BackendFlushResult(
                    backend="prometheus",
                    duration_ms=(perf_counter() - started_at) * 1000.0,
                    points_total=len(samples),
                    failed=False,
                )
            ]
        except Exception as exc:
            if self._logger is not None and hasattr(self._logger, "warning"):
                self._logger.warning(
                    "prometheus_metric_flush_failed",
                    metric_count=len(batch),
                    error=str(exc),
                )
            return [
                BackendFlushResult(
                    backend="prometheus",
                    duration_ms=(perf_counter() - started_at) * 1000.0,
                    points_total=len(batch),
                    failed=True,
                    error=str(exc),
                )
            ]

    def _emit(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self.flush_entries([MetricEntry(kind="metric", name=name, value=float(value), labels=labels)])

    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(value), labels)

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(value), labels)

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(ms), labels)

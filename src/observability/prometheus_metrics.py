from __future__ import annotations

from typing import Any

from src.infra.yc_prometheus import (
    build_prometheus_metric_sample,
    write_prometheus_remote_write,
)
from src.observability.metrics import MetricsClient


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

    def _emit(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        metric_name = str(name or "").strip()
        if not metric_name or not self._endpoint_write or not self._api_key:
            return
        try:
            sample = build_prometheus_metric_sample(
                name=metric_name,
                value=float(value),
                labels=labels,
                service_label=self._service_label,
                namespace=self._namespace,
            )
            write_prometheus_remote_write(
                endpoint_write=self._endpoint_write,
                metrics=[sample],
                bearer_token=self._api_key,
                timeout_seconds=self._timeout_seconds,
            )
        except Exception as exc:
            if self._logger is not None and hasattr(self._logger, "warning"):
                self._logger.warning(
                    "prometheus_metric_emit_failed",
                    metric=metric_name,
                    error=str(exc),
                )

    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(value), labels)

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(value), labels)

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(ms), labels)

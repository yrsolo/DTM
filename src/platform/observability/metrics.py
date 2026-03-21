from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable

from src.platform.integrations.yandex_cloud.monitoring import build_metric_point, write_metrics


@dataclass(frozen=True, slots=True)
class MetricEntry:
    kind: str
    name: str
    value: float
    labels: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class BackendFlushResult:
    backend: str
    duration_ms: float
    points_total: int
    failed: bool = False
    error: str = ""


class MetricsClient:
    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        raise NotImplementedError

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        raise NotImplementedError

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        raise NotImplementedError

    def flush_entries(self, entries: list[MetricEntry]) -> list[BackendFlushResult]:
        raise NotImplementedError


class NoopMetricsClient(MetricsClient):
    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        return

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        return

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        return

    def flush_entries(self, entries: list[MetricEntry]) -> list[BackendFlushResult]:
        return []


class YandexMonitoringMetricsClient(MetricsClient):
    """Best-effort Yandex Monitoring backend for custom metrics."""

    def __init__(
        self,
        folder_id: str,
        iam_token_provider: Callable[[], str],
        logger: Any,
        *,
        endpoint_write: str,
        service_label: str,
        namespace: str,
        timeout_seconds: float = 2.0,
    ) -> None:
        self._folder_id = str(folder_id or "").strip()
        self._iam_token_provider = iam_token_provider
        self._logger = logger
        self._endpoint_write = str(endpoint_write or "").strip()
        self._service_label = str(service_label or "").strip() or "dtm"
        self._namespace = str(namespace or "").strip() or "dtm"
        self._timeout_seconds = max(0.1, float(timeout_seconds))

    def flush_entries(self, entries: list[MetricEntry]) -> list[BackendFlushResult]:
        batch = [entry for entry in list(entries or []) if str(entry.name or "").strip()]
        if not batch or not self._folder_id or not self._endpoint_write:
            return []
        started_at = perf_counter()
        try:
            iam_token = str(self._iam_token_provider() or "").strip()
            if not iam_token:
                raise RuntimeError("iam_token_missing")
            points = [
                build_metric_point(
                    name=str(entry.name).strip(),
                    value=float(entry.value),
                    labels=entry.labels,
                    service_label=self._service_label,
                    namespace=self._namespace,
                )
                for entry in batch
            ]
            write_metrics(
                endpoint_write=self._endpoint_write,
                folder_id=self._folder_id,
                iam_token=iam_token,
                metrics=points,
                timeout_seconds=self._timeout_seconds,
            )
            return [
                BackendFlushResult(
                    backend="monitoring",
                    duration_ms=(perf_counter() - started_at) * 1000.0,
                    points_total=len(points),
                    failed=False,
                )
            ]
        except Exception as exc:
            if self._logger is not None and hasattr(self._logger, "warning"):
                self._logger.warning(
                    "monitoring_metric_flush_failed",
                    metric_count=len(batch),
                    error=str(exc),
                )
            return [
                BackendFlushResult(
                    backend="monitoring",
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

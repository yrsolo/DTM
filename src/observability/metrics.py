from __future__ import annotations

from typing import Any, Callable

from src.infra.yc_monitoring import build_metric_point, write_metrics


class MetricsClient:
    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        raise NotImplementedError

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        raise NotImplementedError

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        raise NotImplementedError


class NoopMetricsClient(MetricsClient):
    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        return

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        return

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        return


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

    def _emit(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        metric_name = str(name or "").strip()
        if not metric_name or not self._folder_id or not self._endpoint_write:
            return
        try:
            iam_token = str(self._iam_token_provider() or "").strip()
            if not iam_token:
                raise RuntimeError("iam_token_missing")
            point = build_metric_point(
                name=metric_name,
                value=float(value),
                labels=labels,
                service_label=self._service_label,
                namespace=self._namespace,
            )
            write_metrics(
                endpoint_write=self._endpoint_write,
                folder_id=self._folder_id,
                iam_token=iam_token,
                metrics=[point],
                timeout_seconds=self._timeout_seconds,
            )
        except Exception as exc:
            if self._logger is not None and hasattr(self._logger, "warning"):
                self._logger.warning(
                    "monitoring_metric_emit_failed",
                    metric=metric_name,
                    error=str(exc),
                )

    def counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(value), labels)

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(value), labels)

    def timing(self, name: str, ms: float, labels: dict[str, str] | None = None) -> None:
        self._emit(name, float(ms), labels)

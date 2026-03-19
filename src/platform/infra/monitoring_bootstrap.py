"""Platform-owned helpers for monitoring and metrics bootstrap."""

from __future__ import annotations

from src.infra.yc_iam import get_iam_token
from src.observability import (
    BufferedMetricsClient,
    CompositeMetricsClient,
    NoopMetricsClient,
    YandexManagedPrometheusRemoteWriteClient,
    YandexMonitoringMetricsClient,
)


def build_metrics_dependencies(ctx, deps: dict, *, structured_logger):
    """Build metrics sink/client wiring without mutating unrelated deps."""

    cfg = ctx.cfg
    monitoring_cfg = cfg.runtime.monitoring
    prometheus_cfg = cfg.runtime.prometheus

    def _iam_token_provider() -> str:
        return get_iam_token(
            deps.get("yc_sa_json_credentials"),
            deps.get("yc_sa_key_file"),
            timeout_seconds=4.0,
        )

    metrics_delivery_mode = str(cfg.runtime.runtime.metrics_delivery_mode or "").strip().lower() or "buffered"
    metrics_sink = NoopMetricsClient()
    metrics_clients = []
    if bool(monitoring_cfg.enabled) and str(monitoring_cfg.backend).strip().lower() == "yandex_monitoring":
        folder_id = str(monitoring_cfg.folder_id).strip() or str(cfg.deploy.yandex_cloud.folder_id).strip()
        metrics_clients.append(
            YandexMonitoringMetricsClient(
                folder_id=folder_id,
                iam_token_provider=_iam_token_provider,
                logger=structured_logger,
                endpoint_write=str(monitoring_cfg.endpoint_write).strip(),
                service_label=str(monitoring_cfg.service).strip() or "dtm",
                namespace=str(monitoring_cfg.namespace).strip() or "dtm",
            )
        )
    if bool(prometheus_cfg.enabled):
        backend_name = str(prometheus_cfg.backend or "").strip().lower()
        if backend_name == "yandex_managed_prometheus":
            prometheus_api_key = str(deps.get("yandex_prometheus_api_key") or "").strip()
            if not prometheus_api_key:
                raise ValueError(
                    "YANDEX_PROMETHEUS_API_KEY or YMP_API_KEY is required "
                    "when prometheus.backend=yandex_managed_prometheus and prometheus.enabled=true"
                )
            metrics_clients.append(
                YandexManagedPrometheusRemoteWriteClient(
                    endpoint_write=str(prometheus_cfg.endpoint_write).strip(),
                    api_key=prometheus_api_key,
                    logger=structured_logger,
                    service_label=str(prometheus_cfg.service).strip() or "dtm",
                    namespace=str(prometheus_cfg.namespace).strip() or "dtm",
                    timeout_seconds=float(prometheus_cfg.timeout_seconds),
                )
            )
        else:
            raise ValueError(f"Unsupported prometheus backend: {backend_name}")
    if len(metrics_clients) == 1:
        metrics_sink = metrics_clients[0]
    elif len(metrics_clients) > 1:
        metrics_sink = CompositeMetricsClient(metrics_clients)
    if metrics_delivery_mode == "off":
        return {
            "metrics_client": NoopMetricsClient(),
            "metrics_sink": NoopMetricsClient(),
        }
    return {
        "metrics_client": BufferedMetricsClient(metrics_sink),
        "metrics_sink": metrics_sink,
    }

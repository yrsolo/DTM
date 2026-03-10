from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import src.app.bootstrap as bootstrap_module
from src.observability import (
    CompositeMetricsClient,
    NoopMetricsClient,
    YandexManagedPrometheusRemoteWriteClient,
    YandexMonitoringMetricsClient,
)


def _fake_cfg(enabled: bool):
    return SimpleNamespace(
        runtime=SimpleNamespace(
            runtime=SimpleNamespace(env_default="test"),
            monitoring=SimpleNamespace(
                enabled=enabled,
                backend="yandex_monitoring",
                folder_id="folder-test",
                endpoint_write="https://monitoring.api.cloud.yandex.net/monitoring/v2/data/write",
                service="custom",
                namespace="dtm",
            ),
            prometheus=SimpleNamespace(
                enabled=False,
                backend="yandex_managed_prometheus",
                endpoint_write="",
                folder_id="",
                workspace_id_test="",
                workspace_id_prod="",
                service="dtm",
                namespace="dtm",
                timeout_seconds=2.0,
            ),
            queue=SimpleNamespace(enabled=False),
        ),
        deploy=SimpleNamespace(yandex_cloud=SimpleNamespace(folder_id="folder-deploy")),
    )


class BootstrapMonitoringTestCase(unittest.TestCase):
    @patch.object(bootstrap_module, "load_config", autospec=True)
    def test_build_app_context_uses_noop_metrics_client_when_monitoring_disabled(self, load_config_mock) -> None:
        load_config_mock.return_value = _fake_cfg(False)
        ctx = bootstrap_module.build_app_context()
        self.assertIsInstance(ctx.deps["metrics_client"], NoopMetricsClient)

    @patch.object(bootstrap_module, "load_config", autospec=True)
    def test_build_app_context_uses_yandex_monitoring_client_when_enabled(self, load_config_mock) -> None:
        load_config_mock.return_value = _fake_cfg(True)
        ctx = bootstrap_module.build_app_context()
        self.assertIsInstance(ctx.deps["metrics_client"], YandexMonitoringMetricsClient)

    @patch.object(bootstrap_module, "load_config", autospec=True)
    def test_build_app_context_uses_prometheus_client_when_enabled(self, load_config_mock) -> None:
        cfg = _fake_cfg(False)
        cfg.runtime.prometheus.enabled = True
        cfg.runtime.prometheus.endpoint_write = (
            "https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/write"
        )
        load_config_mock.return_value = cfg
        with patch.dict(bootstrap_module.os.environ, {"YANDEX_PROMETHEUS_API_KEY": "api-key-test"}, clear=False):
            ctx = bootstrap_module.build_app_context()
        self.assertIsInstance(ctx.deps["metrics_client"], YandexManagedPrometheusRemoteWriteClient)

    @patch.object(bootstrap_module, "load_config", autospec=True)
    def test_build_app_context_uses_composite_client_when_both_backends_enabled(self, load_config_mock) -> None:
        cfg = _fake_cfg(True)
        cfg.runtime.prometheus.enabled = True
        cfg.runtime.prometheus.endpoint_write = (
            "https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/write"
        )
        load_config_mock.return_value = cfg
        with patch.dict(bootstrap_module.os.environ, {"YANDEX_PROMETHEUS_API_KEY": "api-key-test"}, clear=False):
            ctx = bootstrap_module.build_app_context()
        self.assertIsInstance(ctx.deps["metrics_client"], CompositeMetricsClient)

    @patch.object(bootstrap_module, "load_config", autospec=True)
    def test_build_app_context_fails_without_prometheus_api_key_when_enabled(self, load_config_mock) -> None:
        cfg = _fake_cfg(False)
        cfg.runtime.prometheus.enabled = True
        cfg.runtime.prometheus.endpoint_write = (
            "https://monitoring.api.cloud.yandex.net/prometheus/workspaces/workspace-test/api/v1/write"
        )
        load_config_mock.return_value = cfg
        with patch.dict(
            bootstrap_module.os.environ,
            {"YANDEX_PROMETHEUS_API_KEY": "", "YMP_API_KEY": ""},
            clear=False,
        ):
            with self.assertRaisesRegex(ValueError, "YANDEX_PROMETHEUS_API_KEY or YMP_API_KEY"):
                bootstrap_module.build_app_context()


if __name__ == "__main__":
    unittest.main()

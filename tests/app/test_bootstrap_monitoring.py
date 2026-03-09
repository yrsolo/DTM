from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import src.app.bootstrap as bootstrap_module
from src.observability import NoopMetricsClient, YandexMonitoringMetricsClient


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


if __name__ == "__main__":
    unittest.main()

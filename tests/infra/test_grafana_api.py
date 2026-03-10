from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from src.infra.grafana_api import upsert_prometheus_datasource


class GrafanaApiTestCase(unittest.TestCase):
    @patch("src.infra.grafana_api.requests.post")
    @patch("src.infra.grafana_api.requests.get")
    def test_upsert_prometheus_datasource_creates_when_missing(self, get_mock: Mock, post_mock: Mock) -> None:
        get_mock.return_value = Mock(status_code=404)
        create_response = Mock()
        create_response.json.return_value = {"id": 12, "uid": "ds-test"}
        create_response.raise_for_status.return_value = None
        post_mock.return_value = create_response

        result = upsert_prometheus_datasource(
            base_url="http://grafana.test",
            api_token="grafana-token",
            name="DTM YMP Test",
            datasource_url="https://monitoring.api.cloud.yandex.net/prometheus/workspaces/ws-test/api/v1/query",
            bearer_token="ymp-api-key",
        )

        self.assertEqual(result["uid"], "ds-test")
        payload = post_mock.call_args.kwargs["json"]
        self.assertEqual(payload["name"], "DTM YMP Test")
        self.assertEqual(payload["type"], "prometheus")
        self.assertEqual(payload["secureJsonData"]["httpHeaderValue1"], "Bearer ymp-api-key")

    @patch("src.infra.grafana_api.requests.put")
    @patch("src.infra.grafana_api.requests.get")
    def test_upsert_prometheus_datasource_updates_existing(self, get_mock: Mock, put_mock: Mock) -> None:
        get_response = Mock(status_code=200)
        get_response.json.return_value = {"id": 17, "uid": "existing-ds"}
        get_mock.return_value = get_response
        put_response = Mock()
        put_response.json.return_value = {"id": 17, "uid": "existing-ds"}
        put_response.raise_for_status.return_value = None
        put_mock.return_value = put_response

        result = upsert_prometheus_datasource(
            base_url="http://grafana.test",
            api_token="grafana-token",
            name="DTM YMP Test",
            datasource_url="https://monitoring.api.cloud.yandex.net/prometheus/workspaces/ws-test/api/v1/query",
            bearer_token="ymp-api-key",
        )

        self.assertEqual(result["uid"], "existing-ds")
        payload = put_mock.call_args.kwargs["json"]
        self.assertEqual(payload["id"], 17)
        self.assertEqual(payload["url"], "https://monitoring.api.cloud.yandex.net/prometheus/workspaces/ws-test/api/v1/query")


if __name__ == "__main__":
    unittest.main()

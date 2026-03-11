from __future__ import annotations

import unittest

from src.infra.datalens_api import build_dashboard_entry, datalens_dashboard_url, get_datalens_headers
from src.infra.datalens_specs import build_test_ops_dashboard_spec


class DataLensApiHelpersTestCase(unittest.TestCase):
    def test_headers_include_required_auth_fields(self) -> None:
        headers = get_datalens_headers("iam-token", "org-1")
        self.assertEqual(headers["x-yacloud-subjecttoken"], "iam-token")
        self.assertEqual(headers["x-dl-org-id"], "org-1")
        self.assertEqual(headers["x-dl-api-version"], "1")

    def test_dashboard_url_builder(self) -> None:
        self.assertEqual(
            datalens_dashboard_url("org-1", "dash-1"),
            "https://datalens.yandex/org-1/dash-1",
        )

    def test_dashboard_entry_contains_widget_tabs_for_all_chart_ids(self) -> None:
        spec = build_test_ops_dashboard_spec("test")
        chart_ids = {item.key: f"chart-{item.key}" for item in spec.charts}
        payload = build_dashboard_entry(spec=spec, chart_ids_by_key=chart_ids)
        tabs = payload["entry"]["data"]["tabs"]
        self.assertEqual(len(tabs), 1)
        widget_items = [item for item in tabs[0]["items"] if item["type"] == "widget"]
        self.assertEqual(len(widget_items), len(spec.charts))


if __name__ == "__main__":
    unittest.main()

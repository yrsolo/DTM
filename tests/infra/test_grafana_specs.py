from __future__ import annotations

import unittest

from src.infra.grafana_api import grafana_dashboard_url, grafana_embed_url
from src.infra.grafana_specs import build_test_grafana_dashboard


class GrafanaSpecsTestCase(unittest.TestCase):
    def test_grafana_dashboard_url_helpers(self) -> None:
        self.assertEqual(
            grafana_dashboard_url("https://grafana.example", "dtm-test-ops"),
            "https://grafana.example/d/dtm-test-ops",
        )
        self.assertIn(
            "?kiosk",
            grafana_embed_url("https://grafana.example", "dtm-test-ops"),
        )

    def test_build_test_grafana_dashboard_contains_snapshot_and_render_panels(self) -> None:
        dashboard = build_test_grafana_dashboard("test")
        self.assertEqual(dashboard["uid"], "dtm-test-ops")
        titles = {panel["title"] for panel in dashboard["panels"]}
        self.assertIn("Snapshot Stage Timings", titles)
        self.assertIn("Render Stage Timings", titles)
        snapshot_panel = next(panel for panel in dashboard["panels"] if panel["title"] == "Snapshot Stage Timings")
        target_exprs = [target["expr"] for target in snapshot_panel["targets"]]
        self.assertTrue(any("dtm_snapshot_fetch_sheet_ms" in expr for expr in target_exprs))
        self.assertTrue(any('env="test"' in expr for expr in target_exprs))


if __name__ == "__main__":
    unittest.main()

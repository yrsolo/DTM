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
        self.assertIn("Snapshot Fetch Last", titles)
        self.assertIn("Snapshot Fetch Avg5", titles)
        self.assertIn("Timeline Total Last", titles)
        self.assertIn("Designers Total Avg5", titles)
        self.assertIn("Orphan Reconcile Last", titles)
        self.assertIn("API Size Last", titles)
        self.assertIn("Info Summary Last", titles)
        self.assertIn("Info Detail Last", titles)
        self.assertIn("Frontend Stage Breakdown", titles)
        self.assertIn("Frontend Route Compare", titles)
        self.assertIn("Frontend Cache Compare", titles)
        self.assertIn("Timeline Wall Clock Last", titles)
        self.assertIn("Designers Wall Clock Last", titles)
        self.assertIn("Snapshot Business Duration", titles)
        self.assertIn("Snapshot Job Wall Clock", titles)
        self.assertIn("Worker Wall Clock", titles)
        self.assertIn("Metrics Flush Total", titles)
        self.assertIn("Metrics Flush Volume", titles)
        self.assertIn("Notify Runtime", titles)
        self.assertIn("Telegram Intake", titles)
        snapshot_panel = next(panel for panel in dashboard["panels"] if panel["title"] == "Snapshot Stage Timings")
        target_exprs = [target["expr"] for target in snapshot_panel["targets"]]
        self.assertTrue(any("dtm_snapshot_fetch_sheet_ms" in expr for expr in target_exprs))
        self.assertTrue(any("dtm_snapshot_orphan_reconcile_ms" in expr for expr in target_exprs))
        self.assertTrue(any('env="test"' in expr for expr in target_exprs))
        self.assertEqual(snapshot_panel["fieldConfig"]["defaults"]["custom"]["showPoints"], "never")
        fetch_last = next(panel for panel in dashboard["panels"] if panel["title"] == "Snapshot Fetch Last")
        self.assertIn("last_over_time(dtm_snapshot_fetch_sheet_ms", fetch_last["targets"][0]["expr"])
        self.assertEqual(fetch_last["gridPos"]["w"], 2)
        self.assertEqual(fetch_last["gridPos"]["h"], 2)
        fetch_avg5 = next(panel for panel in dashboard["panels"] if panel["title"] == "Snapshot Fetch Avg5")
        self.assertEqual(fetch_avg5["targets"][0]["expr"], 'dtm_snapshot_fetch_sheet_ms{env="test",namespace="dtm",service="dtm"}')
        self.assertTrue(fetch_avg5.get("transformations"))
        wall_clock = next(panel for panel in dashboard["panels"] if panel["title"] == "Snapshot Job Wall Clock")
        self.assertIn("dtm_snapshot_job_wall_clock_ms", wall_clock["targets"][0]["expr"])
        api_latency = next(panel for panel in dashboard["panels"] if panel["title"] == "API and Info Latency")
        self.assertEqual(api_latency["gridPos"]["w"], 6)
        api_latency_exprs = [target["expr"] for target in api_latency["targets"]]
        self.assertTrue(any("dtm_api_duration_ms" in expr for expr in api_latency_exprs))
        self.assertTrue(any("dtm_info_summary_ms" in expr for expr in api_latency_exprs))
        self.assertTrue(any("dtm_info_detail_ms" in expr for expr in api_latency_exprs))
        frontend_stages = next(panel for panel in dashboard["panels"] if panel["title"] == "Frontend Stage Breakdown")
        frontend_stage_exprs = [target["expr"] for target in frontend_stages["targets"]]
        self.assertTrue(any("dtm_api_stage_duration_ms" in expr for expr in frontend_stage_exprs))
        self.assertTrue(any('operation="frontend_access"' in expr for expr in frontend_stage_exprs))
        flush_volume = next(panel for panel in dashboard["panels"] if panel["title"] == "Metrics Flush Volume")
        flush_exprs = [target["expr"] for target in flush_volume["targets"]]
        self.assertTrue(any("dtm_metrics_flush_points_total" in expr for expr in flush_exprs))
        self.assertTrue(any("dtm_metrics_flush_failures_total" in expr for expr in flush_exprs))


if __name__ == "__main__":
    unittest.main()

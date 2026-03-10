from __future__ import annotations

import unittest

from src.infra.datalens_specs import build_test_ops_dashboard_spec


class DataLensSpecsTestCase(unittest.TestCase):
    def test_test_dashboard_spec_contains_snapshot_and_render_metrics(self) -> None:
        spec = build_test_ops_dashboard_spec("test")
        queries = "\n".join(item.query for item in spec.charts)
        self.assertIn("dtm.snapshot.fetch_sheet_ms", queries)
        self.assertIn("dtm.snapshot.write_prep_ms", queries)
        self.assertIn("dtm.render.build_plan_ms", queries)
        self.assertIn("dtm.render.write_sheet_ms", queries)
        self.assertIn('env="test"', queries)


if __name__ == "__main__":
    unittest.main()

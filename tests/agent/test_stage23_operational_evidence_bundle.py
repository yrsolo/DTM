"""Unit tests for Stage 23 operational evidence bundle builder."""

from __future__ import annotations

import unittest

from agent.stage23_operational_evidence_bundle import build_operational_evidence_bundle


class Stage23OperationalEvidenceBundleTestCase(unittest.TestCase):
    def test_ready_when_required_checks_pass(self) -> None:
        smoke = {
            "artifact": "stage23_cloud_tri_block_smoke",
            "ok": True,
            "sync_invoke": {"status_code": 200},
            "api": {
                "v1_status_code": 200,
                "v2_status_code": 200,
                "overlap_count": 5,
                "v2_contract_version": "2.0.1",
                "v2_readmodel_source": "",
            },
        }
        bundle = build_operational_evidence_bundle(smoke)
        self.assertTrue(bundle["go_no_go_input_ready"])
        self.assertEqual(bundle["verdict"], "ready")
        self.assertIn("v2_readmodel_source_present", bundle["optional_warnings"])

    def test_not_ready_when_required_checks_fail(self) -> None:
        smoke = {
            "artifact": "stage23_cloud_tri_block_smoke",
            "ok": False,
            "sync_invoke": {"status_code": 500},
            "api": {
                "v1_status_code": 200,
                "v2_status_code": 503,
                "overlap_count": 0,
                "v2_contract_version": "",
            },
        }
        bundle = build_operational_evidence_bundle(smoke)
        self.assertFalse(bundle["go_no_go_input_ready"])
        self.assertEqual(bundle["verdict"], "not_ready")
        self.assertIn("cloud_smoke_ok", bundle["required_failed"])
        self.assertIn("api_v2_status_200", bundle["required_failed"])


if __name__ == "__main__":
    unittest.main()


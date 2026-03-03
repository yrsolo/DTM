"""Tests for readmodel freshness marker helper in main runtime."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import main


class MainReadmodelFreshnessTestCase(unittest.TestCase):
    def test_marker_for_missing_readmodel(self) -> None:
        marker = main._readmodel_freshness_marker(None)
        self.assertFalse(marker["available"])
        self.assertEqual(marker["readmodel_id"], "frontend_v2:default")
        self.assertIsNone(marker["generated_at_utc"])
        self.assertIsNone(marker["age_seconds"])

    def test_marker_for_existing_readmodel(self) -> None:
        generated_at = datetime.now(timezone.utc) - timedelta(seconds=120)
        row = SimpleNamespace(
            readmodel_id="frontend_v2:default",
            generated_at_utc=generated_at,
            built_from_source_hash="abc",
            payload_hash="def",
        )
        marker = main._readmodel_freshness_marker(row)
        self.assertTrue(marker["available"])
        self.assertEqual(marker["readmodel_id"], "frontend_v2:default")
        self.assertEqual(marker["built_from_source_hash"], "abc")
        self.assertEqual(marker["payload_hash"], "def")
        self.assertIsInstance(marker["age_seconds"], int)
        self.assertGreaterEqual(marker["age_seconds"], 0)


if __name__ == "__main__":
    unittest.main()

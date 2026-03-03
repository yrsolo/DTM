"""Tests for shared source-policy matrix."""

from __future__ import annotations

import unittest

from src.services.source_policy import build_source_policy_matrix


class SourcePolicyMatrixTestCase(unittest.TestCase):
    def test_api_reads_ydb_depends_on_readmodel_source(self) -> None:
        ydb_policy = build_source_policy_matrix(
            readmodel_source="ydb",
            notify_source="legacy",
            render_source="legacy",
        )
        legacy_policy = build_source_policy_matrix(
            readmodel_source="legacy",
            notify_source="legacy",
            render_source="legacy",
        )
        self.assertTrue(ydb_policy.api_reads_ydb())
        self.assertFalse(legacy_policy.api_reads_ydb())

    def test_render_and_notify_runtime_modes(self) -> None:
        policy = build_source_policy_matrix(
            readmodel_source="legacy",
            notify_source="ydb",
            render_source="ydb",
        )
        self.assertTrue(policy.render_reads_ydb("timer"))
        self.assertTrue(policy.render_reads_ydb("sync-only"))
        self.assertFalse(policy.render_reads_ydb("morning"))
        self.assertTrue(policy.notify_reads_ydb("morning"))
        self.assertTrue(policy.notify_reads_ydb("test"))
        self.assertFalse(policy.notify_reads_ydb("sync-only"))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from src.snapshot_engine.engine import _resolve_env_prefix


class SnapshotEnginePrefixTestCase(unittest.TestCase):
    def test_resolve_env_placeholder(self) -> None:
        self.assertEqual(
            _resolve_env_prefix("snapshots/{env}/prep/default.json", "test"),
            "snapshots/test/prep/default.json",
        )
        self.assertEqual(
            _resolve_env_prefix("snapshots/{env}/prep/default.json", "prod"),
            "snapshots/prod/prep/default.json",
        )

    def test_keep_value_without_placeholder(self) -> None:
        self.assertEqual(
            _resolve_env_prefix("snapshots/shared/prep/default.json", "test"),
            "snapshots/shared/prep/default.json",
        )


if __name__ == "__main__":
    unittest.main()

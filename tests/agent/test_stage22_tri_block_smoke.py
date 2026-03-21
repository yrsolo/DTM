"""Tests for Stage 22 tri-block parity smoke snapshot."""

from __future__ import annotations

import unittest

from agent.smokes.stage22_tri_block_smoke import build_tri_block_snapshot


class Stage22TriBlockSmokeTestCase(unittest.TestCase):
    def test_snapshot_parity_between_api_and_render(self) -> None:
        snapshot = build_tri_block_snapshot()
        self.assertEqual(snapshot["api_task_ids"], snapshot["render_task_ids"])
        self.assertEqual(snapshot["notify_task_ids"], ["t-1", "t-2"])


if __name__ == "__main__":
    unittest.main()

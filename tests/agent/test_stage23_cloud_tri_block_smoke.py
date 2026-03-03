"""Unit tests for Stage 23 cloud tri-block smoke helpers."""

from __future__ import annotations

import unittest

from agent.stage23_cloud_tri_block_smoke import _extract_v1_task_ids, _extract_v2_task_ids


class Stage23CloudTriBlockSmokeHelpersTestCase(unittest.TestCase):
    def test_extract_v1_task_ids(self) -> None:
        payload = {"tasks": [{"id": "a"}, {"id": "b"}, {"id": "a"}, {}]}
        self.assertEqual(_extract_v1_task_ids(payload), ["a", "b"])

    def test_extract_v2_task_ids(self) -> None:
        payload = {"tasks": [{"id": "x"}, {"id": "y"}, {"id": "x"}, {"id": ""}]}
        self.assertEqual(_extract_v2_task_ids(payload), ["x", "y"])


if __name__ == "__main__":
    unittest.main()

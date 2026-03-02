"""Unit tests for stage parser."""

from __future__ import annotations

import unittest

from src.core.normalize.stage_parser import parse_stages


class StageParserTestCase(unittest.TestCase):
    def test_splits_by_semicolon_and_newline(self) -> None:
        raw = "Черновик 05.03; Финал 08.03\nЭфир 10.03"
        parsed = parse_stages(raw)
        self.assertEqual(parsed, ["Черновик 05.03", "Финал 08.03", "Эфир 10.03"])

    def test_ignores_empty_chunks(self) -> None:
        raw = ";\n  ;   "
        parsed = parse_stages(raw)
        self.assertEqual(parsed, [])


if __name__ == "__main__":
    unittest.main()


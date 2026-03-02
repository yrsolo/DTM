"""Unit tests for dd.mm date inference."""

from __future__ import annotations

import unittest
from datetime import date

from src.core.normalize.date_inference import infer_date


class DateInferenceTestCase(unittest.TestCase):
    def test_infers_anchor_year(self) -> None:
        result = infer_date("05.03", anchor=date(2026, 3, 1))
        self.assertEqual(result.value, date(2026, 3, 5))
        self.assertGreater(result.confidence, 0.0)

    def test_rolls_year_when_monotonic_sequence_requires(self) -> None:
        result = infer_date("02.01", anchor=date(2026, 12, 25), prev=date(2026, 12, 31))
        self.assertEqual(result.value, date(2027, 1, 2))
        self.assertEqual(result.rule, "dd.mm->year_by_anchor_plus_one")

    def test_returns_unparsed_for_invalid_text(self) -> None:
        result = infer_date("xx.yy", anchor=date(2026, 3, 1))
        self.assertIsNone(result.value)
        self.assertEqual(result.rule, "unparsed")


if __name__ == "__main__":
    unittest.main()


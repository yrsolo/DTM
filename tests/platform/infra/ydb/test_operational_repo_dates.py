"""Tests for date normalization helpers in YDB operational repo."""

from __future__ import annotations

import unittest
from datetime import date

from src.platform.infra.ydb.operational_repo import _to_date


class YdbOperationalRepoDatesTestCase(unittest.TestCase):
    def test_parses_day_offset_from_ydb_date(self) -> None:
        self.assertEqual(_to_date(20504), date(2026, 2, 20))

    def test_parses_epoch_seconds_fallback(self) -> None:
        self.assertEqual(_to_date(1_767_225_600), date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()

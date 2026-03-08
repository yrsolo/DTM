from __future__ import annotations

import sys
import unittest
from datetime import date, datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.app.timezone_utils import format_sheet_timestamp, now_in_timezone, today_in_timezone


class TimezoneUtilsTestCase(unittest.TestCase):
    def test_now_in_timezone_returns_aware_datetime(self) -> None:
        value = now_in_timezone("Europe/Moscow")
        self.assertIsInstance(value, datetime)
        self.assertIsNotNone(value.tzinfo)

    def test_today_in_timezone_returns_date(self) -> None:
        value = today_in_timezone("Europe/Moscow")
        self.assertIsInstance(value, date)

    def test_format_sheet_timestamp_returns_display_string(self) -> None:
        value = format_sheet_timestamp(now_in_timezone("Europe/Moscow"))
        self.assertTrue(value)
        self.assertRegex(value, r"^\d{2}:\d{2}\s")


if __name__ == "__main__":
    unittest.main()

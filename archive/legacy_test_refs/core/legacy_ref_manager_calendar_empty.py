"""Tests for calendar manager empty calendar behavior."""

from __future__ import annotations

import unittest

import pandas as pd

from archive.code.legacy_runtime.services.calendar_runtime import CalendarManager


class _Renderer:
    def __init__(self) -> None:
        self.calls = []

    def begin(self):
        self.calls.append("begin")

    def clear_cells(self):
        self.calls.append("clear_cells")

    def update_cell(self, cell_data):
        self.calls.append(("update_cell", cell_data))

    def execute_updates(self):
        self.calls.append("execute_updates")


class CalendarManagerEmptyTestCase(unittest.TestCase):
    def test_calendar_to_dataframe_empty(self) -> None:
        manager = CalendarManager.__new__(CalendarManager)
        df = CalendarManager.calendar_to_dataframe(manager, {})
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

    def test_write_calendar_to_sheet_empty_does_not_crash(self) -> None:
        manager = CalendarManager.__new__(CalendarManager)
        manager.renderer = _Renderer()
        manager.sheet_name = "calendar"
        CalendarManager.write_calendar_to_sheet(manager, {}, min_date="1W")
        self.assertIn("begin", manager.renderer.calls)
        self.assertIn("clear_cells", manager.renderer.calls)
        self.assertIn("execute_updates", manager.renderer.calls)


if __name__ == "__main__":
    unittest.main()


"""Unit tests for tolerant worksheet-to-DataFrame conversion."""

from __future__ import annotations

import unittest

from src.platform.integrations.google_sheets.service import dataframe_from_worksheet_values


class ServiceDataframeParsingTestCase(unittest.TestCase):
    def test_extra_columns_in_rows_do_not_break_dataframe_build(self) -> None:
        worksheet_values = [
            ["col_a", "col_b"],
            ["v1", "v2", "v3_extra"],
            ["v4"],
        ]

        df = dataframe_from_worksheet_values(worksheet_values, header=True)

        self.assertEqual(list(df.columns), ["col_a", "col_b", "__extra_col_3"])
        self.assertEqual(df.iloc[0].to_dict(), {"col_a": "v1", "col_b": "v2", "__extra_col_3": "v3_extra"})
        self.assertEqual(df.iloc[1].to_dict(), {"col_a": "v4", "col_b": "", "__extra_col_3": ""})

    def test_empty_values_produce_empty_dataframe(self) -> None:
        df = dataframe_from_worksheet_values([], header=True)
        self.assertTrue(df.empty)
        self.assertEqual(list(df.columns), [])


if __name__ == "__main__":
    unittest.main()

"""Tests for timing year inference modes in repository parser."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

import pandas as pd

from core.repository import GoogleSheetsTaskRepository, TimingParser


def _build_row(task_id: int, timing: str) -> dict[str, object]:
    return {
        "БРЕНД": "brand",
        "ФОРМАТ": "format",
        "ПРОЕКТ": "project",
        "ЗАКАЗЧИК": "customer",
        "ДИЗАЙНЕР": "designer",
        "Тайминг": timing,
        "Статус": "",
        "color": "#FFFFFF",
        "color_status": "work",
        "name": f"task-{task_id}",
        "id": task_id,
    }


class TimingYearModesTestCase(unittest.TestCase):
    def test_legacy_mode_regression_keeps_expected_year_shift(self) -> None:
        parser = TimingParser(timing_year_mode="legacy")
        timings = parser.parse(
            "25.12 - stage",
            next_task_date=pd.Timestamp("2026-01-10"),
        )
        self.assertEqual(list(timings.keys()), [pd.Timestamp("2025-12-25")])
        self.assertEqual(timings[pd.Timestamp("2025-12-25")], ["stage"])

    def test_anchors_mode_uses_explicit_year(self) -> None:
        parser = TimingParser(timing_year_mode="anchors")
        timings = parser.parse(
            "01.01.2025 stage",
            next_task_date=pd.Timestamp("2026-01-10"),
        )
        self.assertEqual(list(timings.keys()), [pd.Timestamp("2025-01-01")])
        self.assertEqual(timings[pd.Timestamp("2025-01-01")], ["stage"])
        self.assertTrue(
            any(event.get("year_source") == "explicit_anchor" for event in parser.year_resolution_events)
        )

    def test_chain_mode_shifts_future_jan_mar_back_one_year(self) -> None:
        repo = GoogleSheetsTaskRepository(
            sheet_info=SimpleNamespace(spreadsheet_name="stub", get_sheet_name=lambda _name: "tasks"),
            service=SimpleNamespace(),
        )
        repo.timing_parser = TimingParser(timing_year_mode="chain")
        df = pd.DataFrame(
            [
                _build_row(1, "15.12.2026 stage-a\n20.12.2026 stage-b"),
                _build_row(2, "05.01 stage-c\n10.01 stage-d"),
            ]
        )

        repo._df_to_task(df)
        task = repo.tasks[2]
        self.assertEqual(task.min_date, pd.Timestamp("2026-01-05"))
        self.assertEqual(task.max_date, pd.Timestamp("2026-01-10"))
        self.assertTrue(any(event.get("year_source") == "chain_shift" for event in repo.timing_parser.year_resolution_events))


if __name__ == "__main__":
    unittest.main()

"""Tests for timing year inference modes in repository parser."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

import pandas as pd

from core.timing_parser import TimingParser
from src.platform.integrations.google_sheets.task_repository import GoogleSheetsTaskRepository


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
    def test_load_pipeline_keeps_source_id_column_as_task_id(self) -> None:
        class _ServiceStub:
            def get_dataframe(self, spreadsheet_name, worksheet_name, worksheet_range=None, header=True):  # noqa: ANN001, ARG002
                if worksheet_name == "tasks":
                    return pd.DataFrame([_build_row("uuid-task-001", "15.12.2026 stage-a")])
                return pd.DataFrame([["stub"]])

            def get_cell_colors(self, spreadsheet_name, worksheet_name, worksheet_range):  # noqa: ANN001, ARG002
                return ["#FFFFFF"]

        sheet_info = SimpleNamespace(spreadsheet_name="stub", get_sheet_name=lambda name: name)
        repo = GoogleSheetsTaskRepository(
            sheet_info=sheet_info,
            source_sheet_info=sheet_info,
            service=_ServiceStub(),
        )

        repo._load_and_process_data()

        self.assertIn("uuid-task-001", repo.tasks)
        self.assertNotIn(2, repo.tasks)

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

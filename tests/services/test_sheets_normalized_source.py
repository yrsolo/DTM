from __future__ import annotations

import unittest

from src.adapters.google_sheets.task_repository import GoogleSheetsTaskRepository
from src.config.loader import load_config
from src.services.sources.sheets_normalized_source import SheetsNormalizedTaskSource
from utils.service import GoogleSheetInfo


class _FakeSheetsService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def get_worksheet_values(
        self,
        spreadsheet_name: str,
        worksheet_name: str,
        worksheet_range: str = "A1:Z1000",
    ) -> list[list[str]]:
        self.calls.append(("values", worksheet_range))
        return [
            ["БРЕНД", "ФОРМАТ", "ПРОЕКТ", "ЗАКАЗЧИК", "ДИЗАЙНЕР", "Тайминг", "Статус", "id"],
            ["Brand", "Format", "Project", "Customer", "Alice\nBob", "12.03", "work", "task-1"],
        ]

    def get_cell_colors(
        self,
        spreadsheet_name: str,
        worksheet_name: str,
        worksheet_range: str,
    ) -> list[str]:
        self.calls.append(("colors", worksheet_range))
        return ["green"]


class SheetsNormalizedTaskSourceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        cfg = load_config()
        service = _FakeSheetsService()
        sheet_info = GoogleSheetInfo(
            spreadsheet_name="DTM Source",
            sheet_names={"tasks": "ТАБЛИЧКА", "assistant": "Галя"},
        )
        repo = GoogleSheetsTaskRepository(
            sheet_info=sheet_info,
            source_sheet_info=sheet_info,
            service=service,
            timing_year_mode="legacy",
            task_field_map=dict(cfg.tables.field_maps.get("tasks", {})),
            replace_names=dict(cfg.mapping.project_aliases),
            color_status_map=dict(cfg.mapping.status_by_color),
        )
        self.service = service
        self.source = SheetsNormalizedTaskSource(task_repository=repo)

    def test_read_snapshot_reads_values_and_status_colors_only(self) -> None:
        snapshot = self.source.read_snapshot("A1:Z2000")

        self.assertEqual(
            self.service.calls,
            [("values", "A1:Z2000"), ("colors", "A2:A2")],
        )
        self.assertEqual(snapshot["status_colors"], ["green"])
        self.assertEqual(snapshot["colors"], ["green"])

    def test_build_tasks_from_snapshot_does_not_call_google_again(self) -> None:
        snapshot = self.source.read_snapshot("A1:Z2000")
        self.service.calls.clear()

        tasks = self.source.build_tasks_from_snapshot(snapshot)

        self.assertEqual(self.service.calls, [])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(str(tasks[0].id), "task-1")
        self.assertEqual(self.source.task_repository.row_issues, [])


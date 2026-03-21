from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.adapters.google_sheets.task_repository import GoogleSheetsTaskRepository
from src.config.loader import load_config
from src.contexts.snapshot.adapters.sources.sheets_normalized_source import (
    SheetsNormalizedTaskSource,
)


@dataclass(frozen=True)
class _SheetInfo:
    spreadsheet_name: str
    sheet_names: dict[str, str]

    def get_sheet_name(self, key: str) -> str | None:
        return self.sheet_names.get(key)


class _FakeSheetsService:
    def __init__(self, headers: list[str], row: list[str]) -> None:
        self.calls: list[tuple[str, str]] = []
        self._headers = headers
        self._row = row

    def get_worksheet_values(
        self,
        spreadsheet_name: str,
        worksheet_name: str,
        worksheet_range: str = "A1:Z1000",
    ) -> list[list[str]]:
        self.calls.append(("values", worksheet_range))
        return [self._headers, self._row]

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
        task_field_map = dict(cfg.tables.field_maps.get("tasks", {}))
        headers = [
            task_field_map["brand"],
            task_field_map["format_"],
            task_field_map["project_name"],
            task_field_map["customer"],
            task_field_map["designer"],
            task_field_map["raw_timing"],
            task_field_map["status"],
            task_field_map["task_id"],
        ]
        row = ["Brand", "Format", "Project", "Customer", "Alice\nBob", "12.03", "work", "task-1"]
        service = _FakeSheetsService(headers, row)
        sheet_info = _SheetInfo(
            spreadsheet_name="DTM Source",
            sheet_names={"tasks": "TASKS", "assistant": "ASSISTANT"},
        )
        repo = GoogleSheetsTaskRepository(
            sheet_info=sheet_info,
            source_sheet_info=sheet_info,
            service=service,
            timing_year_mode="legacy",
            task_field_map=task_field_map,
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

from __future__ import annotations

import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from src.contexts.rendering.internal import (
    GoogleSheetsPlanWriter,
    RenderRequest,
    RenderUseCase,
    SheetTarget,
)
from src.contexts.snapshot.internal.engine.model import PrepIndexes, PrepSnapshot, TaskSheet, TaskView, Window


class _FakeEngine:
    def __init__(self, prep: PrepSnapshot | None) -> None:
        self._prep = prep

    def get_prep_snapshot(self) -> PrepSnapshot | None:
        return self._prep


class _FakeService:
    def __init__(self) -> None:
        self.updated_cells: list[dict] = []
        self.updated_borders: list[dict] = []
        self.exec_calls: list[str] = []
        self.cleared: list[tuple[str, str]] = []

    def set_spreadsheet_and_worksheet(self, spreadsheet_name: str, worksheet_name: str) -> None:  # noqa: ARG002
        return None

    def clear_cells(self, spreadsheet_name: str, sheet_name: str, range_: str = "A1:ZZ1000") -> None:  # noqa: ARG002
        self.cleared.append((spreadsheet_name, sheet_name))

    def clear_requests(self) -> None:
        return None

    def update_cell(self, spreadsheet_name: str, sheet_name: str, cell_data: dict) -> None:  # noqa: ARG002
        self.updated_cells.append(dict(cell_data))

    def update_borders(self, spreadsheet_name: str, sheet_name: str, border_data: dict) -> None:  # noqa: ARG002
        self.updated_borders.append(dict(border_data))

    def execute_updates(self, spreadsheet_name: str) -> None:
        self.exec_calls.append(spreadsheet_name)


def _task(task_id: str, owner: str, status: str, timings: dict[str, list[str]]) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=f"title-{task_id}",
            owner_id=owner,
            group_id="group-1",
            brand="brand",
            format_="fmt",
            customer="manager",
            raw_timing="raw timing",
            status=status,
            history=f"history-{task_id}",
            timing=timings,
            milestones=[],
        ),
        extra=None,
    )


class RenderV2TestCase(unittest.TestCase):
    def test_usecase_builds_gantt_like_plan(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "1": _task("1", "owner-1", "work", {"2026-03-05": ["ответ"], "2026-03-06": ["анима"]}),
                "2": _task("2", "owner-2", "pre_done", {"2026-03-06": ["сдача"]}),
            },
            indexes=PrepIndexes(),
        )
        plan = RenderUseCase(_FakeEngine(prep)).build_plan(
            RenderRequest(
                window=Window(start=date(2026, 3, 1), end=date(2026, 3, 10)),
                statuses=["work", "pre_done"],
            )
        )
        self.assertGreater(len(plan.values), 10)
        self.assertGreaterEqual(len(plan.borders), 1)
        # Stage labels are preserved from timing text (including "ответ клиента").
        stage_cells = [cell for cell in plan.values if cell.row >= 3 and cell.col >= 2 and str(cell.value)]
        self.assertTrue(any("ОТВЕТ" in str(cell.value) for cell in stage_cells))
        # Timestamp in A1.
        a1 = [cell for cell in plan.values if cell.row == 1 and cell.col == 1]
        self.assertEqual(len(a1), 1)
        # Designer row in column A.
        owner_cells = [cell for cell in plan.values if cell.col == 1 and str(cell.value).startswith("owner-")]
        self.assertGreaterEqual(len(owner_cells), 2)

    def test_usecase_keeps_continuous_task_band_between_min_and_max_dates(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "1": _task("1", "owner-1", "work", {"2026-03-05": ["ответ клиента"], "2026-03-07": ["анима"]}),
            },
            indexes=PrepIndexes(),
        )
        plan = RenderUseCase(_FakeEngine(prep)).build_plan(
            RenderRequest(
                window=Window(start=date(2026, 3, 1), end=date(2026, 3, 10)),
                statuses=["work"],
            )
        )
        # Owner row=2, first task row=3, start at 01.03 -> day 06.03 is col 7.
        mid_day_cells = [cell for cell in plan.values if cell.row == 3 and cell.col == 7]
        self.assertEqual(len(mid_day_cells), 1)
        self.assertEqual(str(mid_day_cells[0].value), "")
        self.assertIsNotNone(mid_day_cells[0].color)

    def test_writer_applies_cells_and_borders(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task("1", "owner-1", "work", {"2026-03-05": ["ответ"]})},
            indexes=PrepIndexes(),
        )
        plan = RenderUseCase(_FakeEngine(prep)).build_plan(
            RenderRequest(window=Window(start=date(2026, 3, 1), end=date(2026, 3, 10)), statuses=["work"])
        )
        service = _FakeService()
        writer = GoogleSheetsPlanWriter(service, SheetTarget("book", "Задачи"))

        result = writer.apply(plan)

        self.assertTrue(result.applied)
        self.assertEqual(result.target_worksheet, "Задачи")
        self.assertGreater(result.cells_written, 0)
        self.assertEqual(len(service.exec_calls), 1)
        self.assertGreater(len(service.updated_cells), 0)
        self.assertGreater(len(service.updated_borders), 0)

    def test_prep_missing_returns_noop_warning(self) -> None:
        plan = RenderUseCase(_FakeEngine(None)).build_plan(RenderRequest())
        service = _FakeService()
        writer = GoogleSheetsPlanWriter(service, SheetTarget("book", "Задачи"))

        result = writer.apply(plan)

        self.assertFalse(result.applied)
        self.assertIn("prep_snapshot_missing", result.warnings)
        self.assertEqual(len(service.exec_calls), 0)


    def test_timestamp_and_today_anchor_use_configured_timezone(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task("1", "owner-1", "work", {"2026-03-05": ["Ð¾Ñ‚Ð²ÐµÑ‚"]})},
            indexes=PrepIndexes(),
        )
        fake_now = datetime(2026, 3, 6, 9, 15, tzinfo=timezone.utc)
        with (
            patch("src.contexts.rendering.internal.usecase.now_in_timezone", return_value=fake_now),
            patch("src.contexts.rendering.internal.usecase.today_in_timezone", return_value=date(2026, 3, 6)),
        ):
            plan = RenderUseCase(_FakeEngine(prep), timezone_name="Europe/Moscow").build_plan(
                RenderRequest(window=None, statuses=["work"])
            )
        a1 = [cell for cell in plan.values if cell.row == 1 and cell.col == 1]
        self.assertEqual(len(a1), 1)
        self.assertEqual(str(a1[0].value), "09:15 March 06")
        today_cells = [cell for cell in plan.values if cell.row == 2 and str(cell.value) == "06.03"]
        self.assertGreaterEqual(len(today_cells), 1)


if __name__ == "__main__":
    unittest.main()

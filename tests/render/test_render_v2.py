from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.render import GoogleSheetsPlanWriter, RenderRequest, RenderUseCase, SheetTarget
from src.snapshot_engine.model import PrepIndexes, PrepSnapshot, TaskSheet, TaskView, Window


class _FakeEngine:
    def __init__(self, prep: PrepSnapshot | None) -> None:
        self._prep = prep

    def get_prep_snapshot(self) -> PrepSnapshot | None:
        return self._prep


class _FakeService:
    def __init__(self) -> None:
        self.executed: list[tuple[str, list[dict]]] = []

    def get_sheet_id_by_name(self, spreadsheet_name: str, worksheet_name: str):  # noqa: ANN201
        if spreadsheet_name == "book" and worksheet_name == "tasks":
            return 11
        return None

    def execute_updates(self, spreadsheet_name: str, requests: list[dict]) -> None:
        self.executed.append((spreadsheet_name, requests))


def _task(task_id: str, owner: str, status: str, end_day: str) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=f"title-{task_id}",
            owner_id=owner,
            group_id="group-1",
            brand="brand",
            format_="fmt",
            customer="customer",
            raw_timing="raw",
            status=status,
            history=f"history-{task_id}",
            timing={end_day: ["stage"]},
            milestones=[],
        ),
        extra=None,
    )


class RenderV2TestCase(unittest.TestCase):
    def test_usecase_builds_sorted_plan_for_active_statuses(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "1": _task("1", "o1", "work", "2026-03-05"),
                "2": _task("2", "o2", "done", "2026-03-10"),
                "3": _task("3", "o1", "pre_done", "2026-03-15"),
            },
            indexes=PrepIndexes(),
        )
        plan = RenderUseCase(_FakeEngine(prep)).build_plan(
            RenderRequest(
                window=Window(start=None, end=None),
                statuses=["work", "pre_done"],
            )
        )
        values = {(cell.row, cell.col): cell.value for cell in plan.values}
        self.assertEqual(values[(1, 1)], "id")
        # newest active task goes first
        self.assertEqual(values[(2, 1)], "3")
        self.assertEqual(values[(3, 1)], "1")
        self.assertEqual(values[(2, 7)], "history-3")

    def test_writer_sends_single_batch_request(self) -> None:
        service = _FakeService()
        writer = GoogleSheetsPlanWriter(service, SheetTarget("book", "tasks"))
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task("1", "o1", "work", "2026-03-05")},
            indexes=PrepIndexes(),
        )
        plan = RenderUseCase(_FakeEngine(prep)).build_plan(
            RenderRequest(window=Window(start=None, end=None), statuses=["work"])
        )

        result = writer.apply(plan)

        self.assertEqual(len(service.executed), 1)
        spreadsheet_name, requests = service.executed[0]
        self.assertEqual(spreadsheet_name, "book")
        self.assertEqual(len(requests), 1)
        update_cells = requests[0].get("updateCells", {})
        self.assertEqual(update_cells.get("range", {}).get("sheetId"), 11)
        self.assertEqual(update_cells.get("fields"), "userEnteredValue")
        self.assertTrue(result.applied)
        self.assertEqual(result.target_worksheet, "tasks")
        self.assertGreaterEqual(result.rows_written, 1)

    def test_writer_returns_noop_when_plan_empty(self) -> None:
        service = _FakeService()
        writer = GoogleSheetsPlanWriter(service, SheetTarget("book", "tasks"))
        result = writer.apply(plan=RenderUseCase(_FakeEngine(None)).build_plan(RenderRequest()))

        self.assertFalse(result.applied)
        self.assertEqual(result.rows_written, 0)
        self.assertEqual(result.cells_written, 0)
        self.assertIn("prep_snapshot_missing", result.warnings)
        self.assertEqual(len(service.executed), 0)


if __name__ == "__main__":
    unittest.main()


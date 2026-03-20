from __future__ import annotations

import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from src.contexts.rendering.internal import DesignersRenderUseCase, RenderRequest
from src.contexts.snapshot.internal.engine.model import PrepIndexes, PrepSnapshot, TaskSheet, TaskView, Window


class _FakeEngine:
    def __init__(self, prep: PrepSnapshot | None) -> None:
        self._prep = prep

    def get_prep_snapshot(self) -> PrepSnapshot | None:
        return self._prep


def _task(task_id: str, owner: str, status: str, timing: dict[str, list[str]]) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=f"title-{task_id}",
            owner_id=owner,
            group_id="group",
            brand="brand",
            format_="fmt",
            customer="manager",
            raw_timing="raw timing",
            status=status,
            history="history",
            timing=timing,
            milestones=[],
        ),
        extra=None,
    )


class DesignersRenderV2TestCase(unittest.TestCase):
    def test_build_plan_with_headers_and_timestamp(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "1": _task("1", "Алемасов Никита", "work", {"2026-03-05": ["анима"]}),
                "2": _task("2", "Левашова Лера", "pre_done", {"2026-03-06": ["финал"]}),
                "3": _task("3", "Левашова Лера", "done", {"2026-03-06": ["финал"]}),
            },
            indexes=PrepIndexes(),
        )
        plan = DesignersRenderUseCase(_FakeEngine(prep)).build_plan(
            RenderRequest(
                window=Window(start=date(2026, 3, 1), end=date(2026, 3, 20)),
                statuses=["work", "pre_done"],
            )
        )
        self.assertGreater(len(plan.values), 0)
        a1 = [cell for cell in plan.values if cell.row == 1 and cell.col == 1]
        self.assertEqual(len(a1), 1)
        headers = [cell for cell in plan.values if cell.row == 2 and cell.col >= 2]
        self.assertEqual(len(headers), 2)
        self.assertTrue(any(str(cell.value) == "Алемасов Никита" for cell in headers))
        self.assertTrue(any(str(cell.value) == "Левашова Лера" for cell in headers))
        task_titles = [str(cell.value) for cell in plan.values if cell.row >= 3 and cell.col >= 2]
        self.assertIn("title-1", task_titles)
        self.assertIn("title-2", task_titles)
        self.assertNotIn("title-3", task_titles)

    def test_empty_snapshot_or_selection_returns_noop_warning(self) -> None:
        empty_plan = DesignersRenderUseCase(_FakeEngine(None)).build_plan(RenderRequest())
        self.assertIn("prep_snapshot_missing", list(empty_plan.warnings or []))

        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task("1", "owner", "done", {"2026-03-01": ["финал"]})},
            indexes=PrepIndexes(),
        )
        filtered_plan = DesignersRenderUseCase(_FakeEngine(prep)).build_plan(
            RenderRequest(statuses=["work"])
        )
        self.assertIn("empty_render_plan", list(filtered_plan.warnings or []))


    def test_timestamp_and_next_due_use_configured_timezone(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task("1", "owner", "work", {"2026-03-06": ["Ð°Ð½Ð¸Ð¼Ð°"]})},
            indexes=PrepIndexes(),
        )
        fake_now = datetime(2026, 3, 6, 8, 45, tzinfo=timezone.utc)
        with (
            patch("src.contexts.rendering.internal.designers_usecase.now_in_timezone", return_value=fake_now),
            patch("src.contexts.rendering.internal.designers_usecase.today_in_timezone", return_value=date(2026, 3, 6)),
        ):
            plan = DesignersRenderUseCase(_FakeEngine(prep), timezone_name="Europe/Moscow").build_plan(
                RenderRequest(statuses=["work"])
            )
        a1 = [cell for cell in plan.values if cell.row == 1 and cell.col == 1]
        self.assertEqual(len(a1), 1)
        self.assertEqual(str(a1[0].value), "08:45 March 06")


if __name__ == "__main__":
    unittest.main()

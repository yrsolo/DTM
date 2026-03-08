from __future__ import annotations

import unittest

from src.render.target_guard import RenderTarget, validate_render_target


class RenderTargetGuardTestCase(unittest.TestCase):
    def test_blocks_tasks_sheet_target(self) -> None:
        ok, warnings = validate_render_target(
            RenderTarget(
                source_spreadsheet="Спонсорские ТНТ",
                target_spreadsheet="Спонсорские ТНТ",
                tasks_sheet_name="ТАБЛИЧКА",
                target_worksheet="ТАБЛИЧКА",
            )
        )
        self.assertFalse(ok)
        self.assertIn("target_worksheet_points_to_source_tasks_sheet", warnings)

    def test_allows_task_calendar_sheet(self) -> None:
        ok, warnings = validate_render_target(
            RenderTarget(
                source_spreadsheet="Спонсорские ТНТ",
                target_spreadsheet="Спонсорские ТНТ",
                tasks_sheet_name="ТАБЛИЧКА",
                target_worksheet="Задачи",
            )
        )
        self.assertTrue(ok)
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from src.contexts.rendering.internal import RenderApplyResult, RenderJob, RenderPlan, RenderRequest


class _Usecase:
    def build_plan(self, req: RenderRequest) -> RenderPlan:  # noqa: ARG002
        return RenderPlan(values=[], borders=[], warnings=["empty_render_plan"])


class _Writer:
    def apply(self, plan: RenderPlan) -> RenderApplyResult:  # noqa: ARG002
        return RenderApplyResult(
            applied=False,
            rows_written=0,
            cells_written=0,
            target_spreadsheet="book",
            target_worksheet="sheet",
            warnings=["empty_render_plan"],
        )


class RenderJobTimingsTestCase(unittest.TestCase):
    def test_run_records_build_write_and_total_timings(self) -> None:
        result = RenderJob(_Usecase(), _Writer()).run(RenderRequest())

        self.assertGreaterEqual(result.build_plan_ms, 0.0)
        self.assertGreaterEqual(result.write_sheet_ms, 0.0)
        self.assertGreaterEqual(result.total_duration_ms, 0.0)


if __name__ == "__main__":
    unittest.main()

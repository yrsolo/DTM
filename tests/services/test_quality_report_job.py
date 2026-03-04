from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from src.entrypoints.jobs.quality_report_job import print_quality_report


class QualityReportJobTestCase(unittest.TestCase):
    def test_prints_quality_summary_line(self) -> None:
        report = {
            "summary": {
                "task_row_issue_count": 1,
                "people_row_issue_count": 2,
                "timing_parse_error_count": 3,
                "reminder_sent_count": 4,
            }
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            print_quality_report(report)
        line = buf.getvalue().strip()
        self.assertIn("quality_report_summary=", line)
        self.assertIn("task_row_issues=1", line)
        self.assertIn("people_row_issues=2", line)


if __name__ == "__main__":
    unittest.main()

"""Readmodel v2 enum projection tests."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

import pandas as pd

from core.api_payload_v2 import build_frontend_api_payload_v2


def _task(task_id: str, timing: dict[str, list[str]]) -> SimpleNamespace:
    parsed = {pd.Timestamp(day): stages for day, stages in timing.items()}
    return SimpleNamespace(
        id=task_id,
        name=f"Task {task_id}",
        designer="Designer",
        status="work",
        color_status="work",
        brand="Brand",
        format_="Format",
        project_name="Project",
        customer="Customer",
        raw_timing="",
        timing=parsed,
        min_date=min(parsed.keys()) if parsed else None,
        max_date=max(parsed.keys()) if parsed else None,
        next_due=min(parsed.keys()) if parsed else None,
    )


class ReadmodelEnumsTestCase(unittest.TestCase):
    def test_milestone_type_contains_only_used_types(self) -> None:
        payload = build_frontend_api_payload_v2(
            tasks=[
                _task("1", {"2026-03-01": ["раскадровка"], "2026-03-02": ["аниматик"]}),
            ],
            people=[],
            env_name="test",
            source_sheet_name="Sheet",
            statuses=["work"],
            limit=100,
            include_people=False,
        )
        milestone_types = payload["entities"]["enums"]["milestoneType"]
        self.assertEqual(set(milestone_types.keys()), {"storyboard", "animatic"})


if __name__ == "__main__":
    unittest.main()


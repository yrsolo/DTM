from __future__ import annotations

import unittest

from src.legacy.entrypoints.jobs.planner_setup_job import PlannerRuntimeBuildRequest, build_planner_runtime
from src.legacy.entrypoints.jobs.source_switch_job import SourceSwitchRequest


class _Deps:
    def __init__(self) -> None:
        self.task_repository = "repo"


class PlannerSetupJobTestCase(unittest.TestCase):
    def test_builds_planner_and_applies_source_switch(self) -> None:
        calls = {"switch": 0}

        def build_deps(*args, **kwargs):  # noqa: ANN001, ARG001
            return _Deps()

        class Planner:
            def __init__(self, *args, **kwargs):  # noqa: ANN001, ARG002
                self.dependencies = kwargs["dependencies"]

        def apply_switch(request: SourceSwitchRequest):
            calls["switch"] += 1
            self.assertEqual(request.render_source, "ydb")
            return True, True

        planner, source_repo = build_planner_runtime(
            PlannerRuntimeBuildRequest(
                key_json={},
                sheet_info={"sheet": "x"},
                dry_run=False,
                mock_external=True,
                cfg={"cfg": 1},
                mode="test",
                render_source="ydb",
                notify_source="legacy",
                ydb_endpoint="ep",
                ydb_database="db",
                ydb_sa_json_credentials=None,
                ydb_sa_key_file=None,
                build_planner_dependencies=build_deps,
                planner_cls=Planner,
                apply_task_source_switches=apply_switch,
                log=lambda _: None,
            )
        )

        self.assertIsInstance(planner, Planner)
        self.assertEqual(source_repo, "repo")
        self.assertEqual(calls["switch"], 1)


if __name__ == "__main__":
    unittest.main()

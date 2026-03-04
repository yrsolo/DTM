from __future__ import annotations

import unittest

from src.entrypoints.jobs.planner_setup_job import build_planner_runtime


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

        def apply_switch(**kwargs):  # noqa: ANN003
            calls["switch"] += 1
            self.assertEqual(kwargs["render_source"], "ydb")
            return True, True

        planner, source_repo = build_planner_runtime(
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

        self.assertIsInstance(planner, Planner)
        self.assertEqual(source_repo, "repo")
        self.assertEqual(calls["switch"], 1)


if __name__ == "__main__":
    unittest.main()

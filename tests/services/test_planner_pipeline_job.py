from __future__ import annotations

import unittest

from src.entrypoints.jobs.planner_pipeline_job import (
    PlannerPipelineContext,
    PlannerPipelineRequest,
    run_planner_pipeline,
)


class _TaskSourceStub:
    def read_snapshot(self, worksheet_range):  # noqa: ANN001
        _ = worksheet_range
        return {"values": [["ID"], ["1"]], "colors": ["#fff"]}

    def build_tasks_from_snapshot(self, full_snapshot):  # noqa: ANN001
        _ = full_snapshot
        return [{"id": "1"}]


class PlannerPipelineJobTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_runs_pipeline_sequence(self) -> None:
        calls = {"use_case": 0, "store_write": 0, "sync": 0, "quality": 0}

        async def run_use_case(planner, mode, allow_sync):  # noqa: ANN001
            calls["use_case"] += 1
            self.assertEqual(mode, "test")
            self.assertTrue(allow_sync)
            return {"summary": {"task_row_issue_count": 0}}

        def run_store_write(**kwargs):  # noqa: ANN003
            calls["store_write"] += 1
            self.assertEqual(len(kwargs["tasks"]), 1)

        def run_sync(**kwargs):  # noqa: ANN003
            calls["sync"] += 1
            self.assertEqual(kwargs["request"].mode, "test")

        def print_quality(report):  # noqa: ANN001
            calls["quality"] += 1
            self.assertIn("summary", report)

        ctx = PlannerPipelineContext(
            task_source=_TaskSourceStub(),
            legacy_blob_write=True,
            app_store_mode="dual_write",
            app_runtime_env="dev",
            migration_store_file="store.json",
            ydb_endpoint="ep",
            ydb_database="db",
            ydb_sa_json_credentials=None,
            ydb_sa_key_file=None,
            ydb_migrate_on_start=False,
            write_legacy_milestones=True,
            pipeline_cfg=object(),
            safe_print=lambda _: None,
            run_planner_use_case=run_use_case,
            run_legacy_store_write=run_store_write,
            run_ydb_sync_readmodel_pipeline=run_sync,
            pipeline_sync_context_factory=lambda **kwargs: kwargs,
            pipeline_sync_request_factory=lambda **kwargs: type("Req", (), kwargs)(),
            task_to_store_record=lambda task: task,
            task_to_operational_payload=lambda task: task,
            build_store=lambda *args, **kwargs: None,  # noqa: ARG005
            print_quality_report=print_quality,
        )
        request = PlannerPipelineRequest(
            planner=object(),
            use_legacy_planner=True,
            mode="test",
            force_refresh=False,
        )
        result = await run_planner_pipeline(ctx, request)
        self.assertEqual(result["summary"]["task_row_issue_count"], 0)
        self.assertEqual(calls["use_case"], 1)
        self.assertEqual(calls["store_write"], 1)
        self.assertEqual(calls["sync"], 1)
        self.assertEqual(calls["quality"], 1)


if __name__ == "__main__":
    unittest.main()

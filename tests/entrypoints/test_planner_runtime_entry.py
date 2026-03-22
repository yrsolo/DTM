from __future__ import annotations

import asyncio
from datetime import date
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.entrypoints.jobs.runtime_context_job import RuntimeContext
from src.entrypoints.runtime import planner_runtime_entry as module
from src.platform.runtime import render_runtime as render_runtime_module


def _fake_ctx():
    return SimpleNamespace(
        deps={
            "key_json": "",
            "sheet_info": {},
            "default_chat_id": None,
        },
        cfg=SimpleNamespace(
            runtime=SimpleNamespace(
                pipeline=SimpleNamespace(force_refresh_default=False),
                runtime=SimpleNamespace(env_default="test", timezone="Europe/Moscow"),
                triggers={},
                notify=SimpleNamespace(
                    llm_mode_default="draft_only",
                    enhance_concurrency=1,
                    send_retry_attempts=1,
                    send_retry_backoff_seconds=0.1,
                    send_retry_backoff_multiplier=1.0,
                    test_chat_id_override="",
                ),
            ),
            llm=SimpleNamespace(
                assistant={"helper_character": ""},
                models={"openai_default": ""},
            ),
            tables=SimpleNamespace(google_sheets={"source_sheet_name_default": "Source Book"}),
        ),
        log=lambda _message: None,
    )


class _FakeReminderRunner:
    def __init__(self, result) -> None:
        self.result = result
        self.requests = []

    async def run(self, request):
        self.requests.append(request)
        return self.result


class _FakeReminderDeliveryApi:
    def __init__(self, *, snapshot_read, runner, today=None) -> None:  # noqa: ANN001
        self._snapshot_read = snapshot_read
        self._runner = runner
        self._today = today

    def snapshot_read_api(self):
        return self._snapshot_read

    def usecase(self, snapshot_read):  # noqa: ANN001
        return snapshot_read

    def formatter(self):
        return "formatter"

    def sender(self):
        return "sender"

    def enhancer(self, *, mock_external: bool):  # noqa: ARG002
        return None

    def today_in_runtime_timezone(self):
        return self._today

    def job_runner(self, **kwargs):  # noqa: ARG002, ANN003
        return self._runner

    def request(self, **kwargs):  # noqa: ANN003
        return SimpleNamespace(**kwargs)


class _FakeTimerPipeline:
    instances = []

    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.requests = []
        self.__class__.instances.append(self)

    def run(self, request):
        self.requests.append(request)
        return None


class _FakeRenderJob:
    timeline_calls = []
    designers_calls = []
    timeline_result = {}
    designers_result = {}

    @classmethod
    def reset(cls) -> None:
        cls.timeline_calls.clear()
        cls.designers_calls.clear()
        cls.timeline_result = {}
        cls.designers_result = {}


class _FakeRenderTimelineJob:
    def __init__(self, _ctx) -> None:
        return None

    def run(self, cmd):
        _FakeRenderJob.timeline_calls.append(dict(cmd.payload))
        return dict(_FakeRenderJob.timeline_result)


class _FakeRenderDesignersJob:
    def __init__(self, _ctx) -> None:
        return None

    def run(self, cmd):
        _FakeRenderJob.designers_calls.append(dict(cmd.payload))
        return dict(_FakeRenderJob.designers_result)


class PlannerRuntimeEntryTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        _FakeTimerPipeline.instances.clear()
        _FakeRenderJob.reset()

    def test_unsupported_mode_returns_explicit_payload(self) -> None:
        ctx = _fake_ctx()

        with patch.object(
            module,
            "resolve_runtime_context",
            return_value=RuntimeContext(mode="weird_mode", mock_external=False, force_refresh=False),
        ), patch.object(
            module,
            "build_sheets_normalized_task_source",
            return_value=object(),
        ), patch.object(
            module,
            "TimerPipeline",
            side_effect=AssertionError("TimerPipeline must not run for unsupported mode"),
        ):
            result = asyncio.run(
                module.run_planner_runtime(
                    module.PlannerRuntimeRequest(
                        mode="weird_mode",
                        app_context=ctx,
                    )
                )
            )

        self.assertEqual(result["artifact"], "dtm_runtime")
        self.assertEqual(result["status"], "unsupported_mode")
        self.assertEqual(result["mode"], "weird_mode")

    def test_reminders_only_returns_reminder_payload_without_timer_pipeline(self) -> None:
        ctx = _fake_ctx()
        reminder_result = SimpleNamespace(
            artifact="reminder_v2",
            status="ok",
            mode="reminders-only",
            groups=[{"assignee": "A"}],
            delivery_counters={"sent": 1},
            enhancement_counters={"draft": 1},
            warnings=["ok"],
            today=date(2026, 3, 19),
            next_workday=date(2026, 3, 20),
        )
        runner = _FakeReminderRunner(reminder_result)
        fake_engine = object()

        with patch.object(
            module,
            "resolve_runtime_context",
            return_value=RuntimeContext(mode="reminders-only", mock_external=False, force_refresh=False),
        ), patch.object(
            module,
            "build_sheets_normalized_task_source",
            return_value=object(),
        ), patch.object(
            module,
            "get_reminder_delivery_api",
            return_value=_FakeReminderDeliveryApi(snapshot_read=fake_engine, runner=runner),
        ), patch.object(
            module,
            "TimerPipeline",
            side_effect=AssertionError("TimerPipeline must not run for reminders-only"),
        ):
            result = asyncio.run(
                module.run_planner_runtime(
                    module.PlannerRuntimeRequest(
                        mode="reminders-only",
                        app_context=ctx,
                    )
                )
            )

        self.assertEqual(result["artifact"], "reminder_v2")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "reminders-only")
        self.assertEqual(result["summary"]["groups"], 1)
        self.assertEqual(runner.requests[0].mode, "reminders-only")

    def test_render_v2_calls_runtime_render_orchestrator_after_timer_pipeline(self) -> None:
        ctx = _fake_ctx()
        execution_order = []

        class _RecordingTimerPipeline(_FakeTimerPipeline):
            def run(self, request):
                execution_order.append(("timer", request.mode))
                return super().run(request)

        def _fake_render_runtime(_ctx, **kwargs):
            execution_order.append(("render", kwargs["mode"]))
            return {"artifact": "render_v2", "status": "ok", "mode": "render_v2"}

        with patch.object(
            module,
            "resolve_runtime_context",
            return_value=RuntimeContext(mode="render_v2", mock_external=False, force_refresh=True),
        ), patch.object(
            module,
            "build_sheets_normalized_task_source",
            return_value=object(),
        ), patch.object(
            module,
            "TimerPipeline",
            _RecordingTimerPipeline,
        ), patch.object(
            module,
            "run_render_runtime",
            side_effect=_fake_render_runtime,
        ):
            result = asyncio.run(
                module.run_planner_runtime(
                    module.PlannerRuntimeRequest(
                        mode="render_v2",
                        app_context=ctx,
                    )
                )
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(execution_order, [("timer", "render_v2"), ("render", "render_v2")])

    def test_render_v2_returns_blocked_payload_for_unsafe_target(self) -> None:
        ctx = _fake_ctx()

        with patch.object(
            module,
            "resolve_runtime_context",
            return_value=RuntimeContext(mode="render_v2", mock_external=False, force_refresh=True),
        ), patch.object(
            module,
            "build_sheets_normalized_task_source",
            return_value=object(),
        ), patch.object(
            module,
            "TimerPipeline",
            _FakeTimerPipeline,
        ), patch.object(
            module,
            "run_render_runtime",
            return_value={
                "artifact": "render_v2",
                "status": "blocked",
                "mode": "render_v2",
                "error": {"code": "render_target_unsafe"},
                "warnings": ["unsafe_target"],
            },
        ):
            result = asyncio.run(
                module.run_planner_runtime(
                    module.PlannerRuntimeRequest(
                        mode="render_v2",
                        app_context=ctx,
                    )
                )
            )

        self.assertEqual(result["artifact"], "render_v2")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["error"]["code"], "render_target_unsafe")
        self.assertIn("unsafe_target", result["warnings"])
        self.assertEqual(len(_FakeTimerPipeline.instances), 1)
        self.assertEqual(_FakeTimerPipeline.instances[0].requests[0].mode, "render_v2")

    def test_render_runtime_aggregates_success_payload_from_both_jobs(self) -> None:
        ctx = _fake_ctx()
        _FakeRenderJob.timeline_result = {
            "artifact": "render_timeline_sheet",
            "status": "ok",
            "render_applied": True,
            "rows_written": 3,
            "cells_written": 10,
            "target_spreadsheet": "Book",
            "target_worksheet": "Ð—Ð°Ð´Ð°Ñ‡Ð¸",
            "warnings": ["timeline_warning"],
        }
        _FakeRenderJob.designers_result = {
            "artifact": "render_designers_sheet",
            "status": "ok",
            "render_applied": False,
            "rows_written": 2,
            "cells_written": 5,
            "target_spreadsheet": "Book",
            "target_worksheet": "Ð”Ð¸Ð·Ð°Ð¹Ð½ÐµÑ€Ñ‹",
            "warnings": ["designers_warning"],
        }

        with patch.object(render_runtime_module, "RenderTimelineJob", _FakeRenderTimelineJob), patch.object(
            render_runtime_module,
            "RenderDesignersJob",
            _FakeRenderDesignersJob,
        ):
            result = render_runtime_module.run_render_runtime(
                ctx,
                mode="render_v2",
                force_refresh=True,
                dry_run=False,
                statuses=["work", "pre_done"],
            )

        self.assertEqual(result["artifact"], "render_v2")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["render_applied"])
        self.assertEqual(result["rows_written"], 5)
        self.assertEqual(result["cells_written"], 15)
        self.assertEqual(result["targets"]["task_calendar"]["target_worksheet"], "Ð—Ð°Ð´Ð°Ñ‡Ð¸")
        self.assertEqual(result["targets"]["designers"]["target_worksheet"], "Ð”Ð¸Ð·Ð°Ð¹Ð½ÐµÑ€Ñ‹")
        self.assertEqual(result["warnings"], ["timeline_warning", "designers_warning"])
        self.assertEqual(len(_FakeRenderJob.timeline_calls), 1)
        self.assertEqual(len(_FakeRenderJob.designers_calls), 1)

    def test_render_runtime_short_circuits_when_timeline_is_blocked(self) -> None:
        ctx = _fake_ctx()
        ctx.deps["sheet_info"] = {"tasks_sheet_name": "TASKS"}
        _FakeRenderJob.timeline_result = {
            "artifact": "render_timeline_sheet",
            "status": "blocked",
            "target_spreadsheet": "Book",
            "target_worksheet": "Ð—Ð°Ð´Ð°Ñ‡Ð¸",
            "warnings": ["unsafe_timeline"],
        }

        with patch.object(render_runtime_module, "RenderTimelineJob", _FakeRenderTimelineJob), patch.object(
            render_runtime_module,
            "RenderDesignersJob",
            _FakeRenderDesignersJob,
        ):
            result = render_runtime_module.run_render_runtime(
                ctx,
                mode="render_v2",
                force_refresh=False,
                dry_run=True,
                statuses=["work"],
            )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["target_worksheet"], "Ð—Ð°Ð´Ð°Ñ‡Ð¸")
        self.assertEqual(result["error"]["code"], "render_target_unsafe")
        self.assertEqual(len(_FakeRenderJob.timeline_calls), 1)
        self.assertEqual(len(_FakeRenderJob.designers_calls), 0)

    def test_render_runtime_returns_blocked_payload_when_designers_is_blocked(self) -> None:
        ctx = _fake_ctx()
        ctx.deps["sheet_info"] = {"tasks_sheet_name": "TASKS"}
        _FakeRenderJob.timeline_result = {
            "artifact": "render_timeline_sheet",
            "status": "ok",
            "render_applied": True,
            "rows_written": 1,
            "cells_written": 2,
            "target_spreadsheet": "Book",
            "target_worksheet": "Ð—Ð°Ð´Ð°Ñ‡Ð¸",
            "warnings": [],
        }
        _FakeRenderJob.designers_result = {
            "artifact": "render_designers_sheet",
            "status": "blocked",
            "target_spreadsheet": "Book",
            "target_worksheet": "Ð”Ð¸Ð·Ð°Ð¹Ð½ÐµÑ€Ñ‹",
            "warnings": ["unsafe_designers"],
        }

        with patch.object(render_runtime_module, "RenderTimelineJob", _FakeRenderTimelineJob), patch.object(
            render_runtime_module,
            "RenderDesignersJob",
            _FakeRenderDesignersJob,
        ):
            result = render_runtime_module.run_render_runtime(
                ctx,
                mode="render_v2",
                force_refresh=False,
                dry_run=False,
                statuses=["work", "pre_done"],
            )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["target_worksheet"], "Ð”Ð¸Ð·Ð°Ð¹Ð½ÐµÑ€Ñ‹")
        self.assertEqual(result["warnings"], ["unsafe_designers"])
        self.assertEqual(len(_FakeRenderJob.timeline_calls), 1)
        self.assertEqual(len(_FakeRenderJob.designers_calls), 1)


if __name__ == "__main__":
    unittest.main()


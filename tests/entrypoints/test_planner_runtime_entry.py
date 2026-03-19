from __future__ import annotations

import asyncio
from datetime import date
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.entrypoints.jobs.runtime_context_job import RuntimeContext
from src.entrypoints.runtime import planner_runtime_entry as module


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


class _FakeTimerPipeline:
    instances = []

    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.requests = []
        self.__class__.instances.append(self)

    def run(self, request):
        self.requests.append(request)
        return None


class PlannerRuntimeEntryTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        _FakeTimerPipeline.instances.clear()

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
            "build_snapshot_engine",
            return_value=fake_engine,
        ), patch.object(
            module,
            "_get_reminders_usecase",
            return_value="usecase",
        ), patch.object(
            module,
            "_get_reminders_formatter",
            return_value="formatter",
        ), patch.object(
            module,
            "_get_reminders_sender",
            return_value="sender",
        ), patch.object(
            module,
            "_build_notify_enhancer",
            return_value=None,
        ), patch.object(
            module,
            "_get_reminder_job_runner",
            return_value=runner,
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

    def test_render_v2_returns_blocked_payload_for_unsafe_target(self) -> None:
        ctx = _fake_ctx()
        ctx.deps["sheet_info"] = {"spreadsheet_name": "Target Book"}
        ctx.cfg.tables = SimpleNamespace(google_sheets={"source_sheet_name_default": "Source Book"})

        class _FakeGoogleSheetInfo:
            def __init__(self, **kwargs) -> None:
                self.spreadsheet_name = kwargs.get("spreadsheet_name", "Target Book")

            def get_sheet_name(self, name: str) -> str:
                if name == "task_calendar":
                    return "Tasks"
                if name == "tasks":
                    return "TASKS"
                return ""

        fake_service_module = SimpleNamespace(
            GoogleSheetInfo=_FakeGoogleSheetInfo,
            GoogleSheetsService=object,
        )

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
            "_get_rendering_snapshot_engine",
            return_value=object(),
        ), patch.object(
            module,
            "_get_timeline_usecase",
            return_value="timeline_usecase",
        ), patch.object(
            module,
            "validate_render_target",
            return_value=(False, ["unsafe_target"]),
        ), patch.dict(
            sys.modules,
            {"utils.service": fake_service_module},
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


if __name__ == "__main__":
    unittest.main()

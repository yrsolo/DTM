from __future__ import annotations

import asyncio
import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.jobs.send_reminders_job import SendRemindersJob


class _FakeReminderResult:
    def __init__(self) -> None:
        self.artifact = "reminder_v2"
        self.status = "ok"
        self.mode = "morning"
        self.today = "2026-03-06"
        self.next_workday = "2026-03-09"
        self.groups = [object()]
        self.delivery_counters = {"candidates_total": 1, "sent": 1}
        self.enhancement_counters = {"attempted": 0}
        self.warnings = []


class _FakeReminderJob:
    last_request = None
    run_calls = 0

    def __init__(self, **kwargs):  # noqa: ANN003
        self.kwargs = kwargs

    async def run(self, req):  # noqa: ANN001
        type(self).last_request = req
        type(self).run_calls += 1
        return _FakeReminderResult()


class _FakeSnapshotEngine:
    pass


class _FakeMetrics:
    def __init__(self) -> None:
        self.counters = []
        self.gauges = []
        self.timings = []

    def counter(self, name, value=1, labels=None):  # noqa: ANN001
        self.counters.append((name, value, dict(labels or {})))

    def gauge(self, name, value, labels=None):  # noqa: ANN001
        self.gauges.append((name, value, dict(labels or {})))

    def timing(self, name, value, labels=None):  # noqa: ANN001
        self.timings.append((name, value, dict(labels or {})))


def _ctx():
    return AppContext(
        cfg=SimpleNamespace(
            llm=SimpleNamespace(
                llm={"provider_default": "openai"},
                http={
                    "timeout_seconds_default": 25,
                    "retry_attempts_default": 2,
                    "retry_backoff_seconds_default": 0.8,
                },
                models={"openai_default": "gpt-test"},
                assistant={"helper_character": ""},
            ),
            runtime=SimpleNamespace(
                runtime=SimpleNamespace(env_default="dev", timezone="Europe/Moscow"),
                notify=SimpleNamespace(
                    llm_mode_default="draft_only",
                    enhance_concurrency=2,
                    send_retry_attempts=2,
                    send_retry_backoff_seconds=0.1,
                    send_retry_backoff_multiplier=2.0,
                    test_chat_id_override="",
                ),
            ),
            mapping=SimpleNamespace(hidden_stage_names=[]),
        ),
        deps={
            "metrics_client": _FakeMetrics(),
            "structured_logger": None,
            "tg_bot_token": "token",
            "default_chat_id": "-1",
            "proxy_url": "",
            "openai_token": "",
            "org_token": "",
            "google_llm_api_key": "",
            "yandex_llm_api_key": "",
        },
    )


class SendRemindersJobTestCase(unittest.TestCase):
    def test_morning_skips_on_saturday(self) -> None:
        import src.jobs.send_reminders_job as module

        original_build_snapshot_engine = module.build_snapshot_engine
        original_build_job_runner = module._build_reminder_job_runner
        original_today = module._today_in_runtime_timezone
        _FakeReminderJob.last_request = None
        _FakeReminderJob.run_calls = 0
        module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
        module._build_reminder_job_runner = lambda **kwargs: _FakeReminderJob(**kwargs)  # type: ignore[assignment]
        module._today_in_runtime_timezone = lambda _ctx: date(2026, 3, 7)  # type: ignore[assignment]
        try:
            result = asyncio.run(
                SendRemindersJob(_ctx()).run(
                    Command(
                        job_id="job-1",
                        type="send_reminders",
                        created_at_utc=datetime.now(timezone.utc),
                        requested_by=RequestedBy(source="admin"),
                        payload={"mode": "morning"},
                    )
                )
            )
        finally:
            module.build_snapshot_engine = original_build_snapshot_engine  # type: ignore[assignment]
            module._build_reminder_job_runner = original_build_job_runner  # type: ignore[assignment]
            module._today_in_runtime_timezone = original_today  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "morning")
        self.assertEqual(result["delivery_counters"]["sent"], 0)
        self.assertIn("morning_weekend_skipped", result["warnings"])
        self.assertEqual(_FakeReminderJob.run_calls, 0)

    def test_morning_skips_on_sunday(self) -> None:
        import src.jobs.send_reminders_job as module

        original_build_snapshot_engine = module.build_snapshot_engine
        original_build_job_runner = module._build_reminder_job_runner
        original_today = module._today_in_runtime_timezone
        _FakeReminderJob.run_calls = 0
        module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
        module._build_reminder_job_runner = lambda **kwargs: _FakeReminderJob(**kwargs)  # type: ignore[assignment]
        module._today_in_runtime_timezone = lambda _ctx: date(2026, 3, 8)  # type: ignore[assignment]
        try:
            result = asyncio.run(
                SendRemindersJob(_ctx()).run(
                    Command(
                        job_id="job-2",
                        type="send_reminders",
                        created_at_utc=datetime.now(timezone.utc),
                        requested_by=RequestedBy(source="admin"),
                        payload={"mode": "morning"},
                    )
                )
            )
        finally:
            module.build_snapshot_engine = original_build_snapshot_engine  # type: ignore[assignment]
            module._build_reminder_job_runner = original_build_job_runner  # type: ignore[assignment]
            module._today_in_runtime_timezone = original_today  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertIn("morning_weekend_skipped", result["warnings"])
        self.assertEqual(_FakeReminderJob.run_calls, 0)

    def test_test_mode_still_runs_on_saturday(self) -> None:
        import src.jobs.send_reminders_job as module

        original_build_snapshot_engine = module.build_snapshot_engine
        original_build_job_runner = module._build_reminder_job_runner
        original_today = module._today_in_runtime_timezone
        _FakeReminderJob.last_request = None
        _FakeReminderJob.run_calls = 0
        module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
        module._build_reminder_job_runner = lambda **kwargs: _FakeReminderJob(**kwargs)  # type: ignore[assignment]
        module._today_in_runtime_timezone = lambda _ctx: date(2026, 3, 7)  # type: ignore[assignment]
        try:
            result = asyncio.run(
                SendRemindersJob(_ctx()).run(
                    Command(
                        job_id="job-3",
                        type="send_reminders",
                        created_at_utc=datetime.now(timezone.utc),
                        requested_by=RequestedBy(source="admin"),
                        payload={"mode": "test"},
                    )
                )
            )
        finally:
            module.build_snapshot_engine = original_build_snapshot_engine  # type: ignore[assignment]
            module._build_reminder_job_runner = original_build_job_runner  # type: ignore[assignment]
            module._today_in_runtime_timezone = original_today  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(_FakeReminderJob.run_calls, 1)
        self.assertEqual(_FakeReminderJob.last_request.mode, "test")

    def test_morning_passes_friday_today_override_to_reminder_request(self) -> None:
        import src.jobs.send_reminders_job as module

        original_build_snapshot_engine = module.build_snapshot_engine
        original_build_job_runner = module._build_reminder_job_runner
        original_today = module._today_in_runtime_timezone
        _FakeReminderJob.last_request = None
        _FakeReminderJob.run_calls = 0
        module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
        module._build_reminder_job_runner = lambda **kwargs: _FakeReminderJob(**kwargs)  # type: ignore[assignment]
        module._today_in_runtime_timezone = lambda _ctx: date(2026, 3, 6)  # type: ignore[assignment]
        try:
            result = asyncio.run(
                SendRemindersJob(_ctx()).run(
                    Command(
                        job_id="job-4",
                        type="send_reminders",
                        created_at_utc=datetime.now(timezone.utc),
                        requested_by=RequestedBy(source="admin"),
                        payload={"mode": "morning"},
                    )
                )
            )
        finally:
            module.build_snapshot_engine = original_build_snapshot_engine  # type: ignore[assignment]
            module._build_reminder_job_runner = original_build_job_runner  # type: ignore[assignment]
            module._today_in_runtime_timezone = original_today  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(_FakeReminderJob.run_calls, 1)
        self.assertEqual(_FakeReminderJob.last_request.today_override.isoformat(), "2026-03-06")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import asyncio
import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

from src.platform.context import AppContext
from src.platform.runtime.commands.model import Command, RequestedBy
from src.contexts.reminders.internal.job_runner import SendRemindersJob


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
    last_kwargs = None
    run_calls = 0

    def __init__(self, **kwargs):  # noqa: ANN003
        self.kwargs = kwargs
        type(self).last_kwargs = kwargs

    async def run(self, req):  # noqa: ANN001
        type(self).last_request = req
        type(self).run_calls += 1
        return _FakeReminderResult()


class _FakeSnapshotEngine:
    pass


class _FakeDeliveryApi:
    def __init__(self) -> None:
        self.snapshot_read = _FakeSnapshotEngine()

    def snapshot_read_api(self):
        return self.snapshot_read

    def usecase(self, snapshot_read):  # noqa: ANN001
        return snapshot_read

    def formatter(self):
        return "formatter"

    def sender(self):
        return "sender"

    def enhancer(self, *, mock_external: bool):  # noqa: ARG002
        return None

    def llm_model_for_mode(self, mode: str):
        if str(mode).strip().lower() == "morning":
            return "gpt-5.5"
        return "gpt-test"

    def today_in_runtime_timezone(self):
        return date(2026, 3, 7)

    def job_runner(self, **kwargs):  # noqa: ANN003
        return _FakeReminderJob(**kwargs)

    def request(self, **kwargs):  # noqa: ANN003
        return SimpleNamespace(**kwargs)


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
        import src.contexts.reminders.internal.job_runner as module

        original_get_delivery_api = module.get_delivery_api
        _FakeReminderJob.last_request = None
        _FakeReminderJob.last_kwargs = None
        _FakeReminderJob.run_calls = 0
        delivery_api = _FakeDeliveryApi()
        module.get_delivery_api = lambda _ctx: delivery_api  # type: ignore[assignment]
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
            module.get_delivery_api = original_get_delivery_api  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "morning")
        self.assertEqual(result["delivery_counters"]["sent"], 0)
        self.assertIn("morning_weekend_skipped", result["warnings"])
        self.assertEqual(_FakeReminderJob.run_calls, 0)

    def test_morning_skips_on_sunday(self) -> None:
        import src.contexts.reminders.internal.job_runner as module

        original_get_delivery_api = module.get_delivery_api
        _FakeReminderJob.run_calls = 0
        delivery_api = _FakeDeliveryApi()
        delivery_api.today_in_runtime_timezone = lambda: date(2026, 3, 8)  # type: ignore[method-assign]
        module.get_delivery_api = lambda _ctx: delivery_api  # type: ignore[assignment]
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
            module.get_delivery_api = original_get_delivery_api  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertIn("morning_weekend_skipped", result["warnings"])
        self.assertEqual(_FakeReminderJob.run_calls, 0)

    def test_test_mode_still_runs_on_saturday(self) -> None:
        import src.contexts.reminders.internal.job_runner as module

        original_get_delivery_api = module.get_delivery_api
        _FakeReminderJob.last_request = None
        _FakeReminderJob.last_kwargs = None
        _FakeReminderJob.run_calls = 0
        delivery_api = _FakeDeliveryApi()
        module.get_delivery_api = lambda _ctx: delivery_api  # type: ignore[assignment]
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
            module.get_delivery_api = original_get_delivery_api  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(_FakeReminderJob.run_calls, 1)
        self.assertEqual(_FakeReminderJob.last_request.mode, "test")
        self.assertEqual(_FakeReminderJob.last_kwargs["llm_model"], "gpt-test")

    def test_morning_passes_friday_today_override_to_reminder_request(self) -> None:
        import src.contexts.reminders.internal.job_runner as module

        original_get_delivery_api = module.get_delivery_api
        _FakeReminderJob.last_request = None
        _FakeReminderJob.last_kwargs = None
        _FakeReminderJob.run_calls = 0
        delivery_api = _FakeDeliveryApi()
        delivery_api.today_in_runtime_timezone = lambda: date(2026, 3, 6)  # type: ignore[method-assign]
        module.get_delivery_api = lambda _ctx: delivery_api  # type: ignore[assignment]
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
            module.get_delivery_api = original_get_delivery_api  # type: ignore[assignment]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(_FakeReminderJob.run_calls, 1)
        self.assertEqual(_FakeReminderJob.last_request.today_override.isoformat(), "2026-03-06")
        self.assertEqual(_FakeReminderJob.last_kwargs["llm_model"], "gpt-5.5")


if __name__ == "__main__":
    unittest.main()



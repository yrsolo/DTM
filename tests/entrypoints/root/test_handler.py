from __future__ import annotations

import unittest

from src.entrypoints.root.handler import handle


class _FakeHttpShell:
    def __init__(self) -> None:
        self.calls: list[tuple[dict, dict, bool]] = []

    async def handle(self, event, payload, is_http_event):
        self.calls.append((event, payload, is_http_event))
        return {"statusCode": 200, "body": "http"}


class _FakeWorkerShell:
    def __init__(self) -> None:
        self.calls: list[object] = []

    async def handle_queue_event(self, event):
        self.calls.append(event)
        return {"statusCode": 200, "body": "queue"}


class _FakeTriggerShell:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    async def handle_trigger(self, trigger_mode, event):
        self.calls.append((trigger_mode, event))
        return {"statusCode": 200, "body": trigger_mode}


class HandlerTopPathTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_routes_http_directly_to_http_shell(self) -> None:
        http_shell = _FakeHttpShell()
        worker_shell = _FakeWorkerShell()
        trigger_shell = _FakeTriggerShell()

        response = await handle(
            {"path": "/info", "httpMethod": "GET"},
            None,
            handle_http_event=http_shell.handle,
            handle_queue_event=worker_shell.handle_queue_event,
            handle_trigger_event=trigger_shell.handle_trigger,
            get_trigger_modes=lambda: {},
        )

        self.assertEqual(response["body"], "http")
        self.assertEqual(len(http_shell.calls), 1)
        self.assertEqual(worker_shell.calls, [])
        self.assertEqual(trigger_shell.calls, [])

    async def test_routes_queue_directly_to_worker_shell(self) -> None:
        http_shell = _FakeHttpShell()
        worker_shell = _FakeWorkerShell()
        trigger_shell = _FakeTriggerShell()
        event = {
            "messages": [
                {
                    "details": {
                        "message": {
                            "body": '{"job_id":"j1"}',
                        }
                    }
                }
            ]
        }

        response = await handle(
            event,
            None,
            handle_http_event=http_shell.handle,
            handle_queue_event=worker_shell.handle_queue_event,
            handle_trigger_event=trigger_shell.handle_trigger,
            get_trigger_modes=lambda: {},
        )

        self.assertEqual(response["body"], "queue")
        self.assertEqual(worker_shell.calls, [event])
        self.assertEqual(http_shell.calls, [])
        self.assertEqual(trigger_shell.calls, [])

    async def test_routes_timer_trigger_directly_to_trigger_shell(self) -> None:
        http_shell = _FakeHttpShell()
        worker_shell = _FakeWorkerShell()
        trigger_shell = _FakeTriggerShell()
        event = {"messages": [{"details": {"trigger_id": "trigger-1"}}]}

        response = await handle(
            event,
            None,
            handle_http_event=http_shell.handle,
            handle_queue_event=worker_shell.handle_queue_event,
            handle_trigger_event=trigger_shell.handle_trigger,
            get_trigger_modes=lambda: {"trigger-1": "timer"},
        )

        self.assertEqual(response["body"], "timer")
        self.assertEqual(trigger_shell.calls, [("timer", event)])
        self.assertEqual(http_shell.calls, [])
        self.assertEqual(worker_shell.calls, [])

    async def test_returns_healthcheck_without_shells(self) -> None:
        response = await handle(
            {"body": {"healthcheck": True}},
            None,
            handle_http_event=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("http shell should not be used")),
            handle_queue_event=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("worker shell should not be used")),
            handle_trigger_event=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("trigger shell should not be used")),
            get_trigger_modes=lambda: (_ for _ in ()).throw(AssertionError("trigger modes should not be resolved")),
            get_telegram_webhook_path=lambda: (_ for _ in ()).throw(
                AssertionError("telegram webhook path should not be resolved")
            ),
        )

        self.assertEqual(response, {"statusCode": 200, "body": "!HEALTHY!"})

    async def test_resolves_telegram_webhook_path_only_for_http_events(self) -> None:
        http_shell = _FakeHttpShell()
        worker_shell = _FakeWorkerShell()
        trigger_shell = _FakeTriggerShell()
        calls: list[str] = []

        response = await handle(
            {"path": "/custom-telegram", "httpMethod": "POST"},
            None,
            handle_http_event=http_shell.handle,
            handle_queue_event=worker_shell.handle_queue_event,
            handle_trigger_event=trigger_shell.handle_trigger,
            get_trigger_modes=lambda: {},
            get_telegram_webhook_path=lambda: calls.append("resolved") or "/custom-telegram",
        )

        self.assertEqual(response["body"], "http")
        self.assertEqual(calls, ["resolved"])


if __name__ == "__main__":
    unittest.main()

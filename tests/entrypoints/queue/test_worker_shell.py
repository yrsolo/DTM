from __future__ import annotations

import asyncio
import json
import unittest
from types import SimpleNamespace

from src.entrypoints.queue.worker_shell import WorkerShell


class _FakeWorker:
    def __init__(self, result: dict) -> None:
        self._result = result

    async def run_once_from_messages(self, _messages):
        return dict(self._result)


class WorkerShellTestCase(unittest.TestCase):
    def test_worker_shell_returns_503_when_retry_is_requested(self) -> None:
        ctx = SimpleNamespace(deps={"command_worker": _FakeWorker({"artifact": "command_worker", "retry_requested": True})})
        response = asyncio.run(WorkerShell(ctx).handle_queue_event({"messages": []}))
        self.assertEqual(response["statusCode"], 503)

    def test_worker_shell_returns_200_for_terminal_failures_only(self) -> None:
        ctx = SimpleNamespace(
            deps={
                "command_worker": _FakeWorker(
                    {
                        "artifact": "command_worker",
                        "status": "partial_failure",
                        "retry_requested": False,
                        "terminal_failed": 1,
                    }
                )
            }
        )
        response = asyncio.run(WorkerShell(ctx).handle_queue_event({"messages": []}))
        self.assertEqual(response["statusCode"], 200)
        payload = json.loads(response["body"])
        self.assertEqual(payload["status"], "partial_failure")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from src.entrypoints.root.modes import Mode
from src.entrypoints.root.parse_request import parse_request


class ParseRequestTestCase(unittest.TestCase):
    def test_classifies_queue_worker_mode(self) -> None:
        parsed = parse_request(
            {
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
        )
        self.assertEqual(parsed.mode, Mode.QUEUE_WORKER)

    def test_classifies_healthcheck_mode(self) -> None:
        parsed = parse_request({"body": {"healthcheck": True}})
        self.assertEqual(parsed.mode, Mode.HEALTHCHECK)

    def test_classifies_http_access_api_mode(self) -> None:
        parsed = parse_request({"path": "/info", "httpMethod": "GET"})
        self.assertEqual(parsed.mode, Mode.HTTP_ACCESS_API)
        self.assertEqual(parsed.path, "/info")

    def test_classifies_telegram_webhook_mode(self) -> None:
        parsed = parse_request({"path": "/telegram", "httpMethod": "POST"})
        self.assertEqual(parsed.mode, Mode.TELEGRAM_WEBHOOK)

    def test_classifies_timer_trigger_mode(self) -> None:
        parsed = parse_request(
            {"messages": [{"details": {"trigger_id": "trigger-1"}}]},
            get_trigger_modes=lambda: {"trigger-1": "timer"},
        )
        self.assertEqual(parsed.mode, Mode.TRIGGER_TIMER)

    def test_classifies_morning_trigger_mode(self) -> None:
        parsed = parse_request(
            {"messages": [{"details": {"trigger_id": "trigger-2"}}]},
            get_trigger_modes=lambda: {"trigger-2": "morning"},
        )
        self.assertEqual(parsed.mode, Mode.TRIGGER_MORNING)

    def test_classifies_unknown_mode(self) -> None:
        parsed = parse_request({"foo": "bar"})
        self.assertEqual(parsed.mode, Mode.UNKNOWN)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from src.entrypoints.event_classifier import EventKind, classify_event


class EntrypointDispatcherClassifierTestCase(unittest.TestCase):
    def test_classifies_queue_event(self) -> None:
        result = classify_event(
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
            },
            triggers={},
        )
        self.assertEqual(result.kind, EventKind.QUEUE)

    def test_classifies_healthcheck_event(self) -> None:
        result = classify_event({"body": {"healthcheck": True}}, triggers={})
        self.assertEqual(result.kind, EventKind.HEALTHCHECK)

    def test_classifies_http_event(self) -> None:
        result = classify_event({"path": "/info", "httpMethod": "GET"}, triggers={})
        self.assertEqual(result.kind, EventKind.HTTP)

    def test_classifies_trigger_event(self) -> None:
        result = classify_event(
            {"messages": [{"details": {"trigger_id": "trigger-1"}}]},
            triggers={"trigger-1": "timer"},
        )
        self.assertEqual(result.kind, EventKind.TRIGGER)
        self.assertEqual(result.trigger_mode, "timer")

    def test_classifies_unknown_event(self) -> None:
        result = classify_event({"foo": "bar"}, triggers={})
        self.assertEqual(result.kind, EventKind.UNKNOWN)


if __name__ == "__main__":
    unittest.main()

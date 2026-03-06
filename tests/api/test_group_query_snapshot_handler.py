from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.group_query_handler import GroupQueryHandler


class _FakeNotifier:
    sent = []

    def __init__(self, bot_token=None, default_chat_id=None) -> None:  # noqa: ANN001, D401
        _ = bot_token, default_chat_id

    async def send_message(self, chat_id, text, parse_mode=None):  # noqa: ANN001
        self.sent.append((chat_id, text, parse_mode))
        return None


class _FakeSnapshotEngine:
    def frontend_v2(self, query):  # noqa: ANN001
        _ = query
        return {
            "entities": {
                "people": [{"id": "owner-1", "name": "Иван Иванов"}],
            },
            "tasks": [
                {
                    "id": "t1",
                    "title": "Задача 1",
                    "ownerId": "owner-1",
                    "date": {"end": "2026-03-10"},
                    "milestones": [{"type": "feedback", "planned": "2026-03-10"}],
                }
            ],
        }


class GroupQuerySnapshotHandlerTestCase(unittest.TestCase):
    def test_group_query_uses_snapshot_engine_payload(self) -> None:
        import src.entrypoints.http.group_query_handler as module

        orig_build_snapshot_engine = module.build_snapshot_engine
        orig_notifier = module.TelegramNotifier
        try:
            module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
            module.TelegramNotifier = _FakeNotifier  # type: ignore[assignment]
            _FakeNotifier.sent = []

            ctx = AppContext(
                cfg=SimpleNamespace(),
                deps={"tg_bot_username": "@dtm_bot", "tg_bot_token": "x", "default_chat_id": "0"},
            )
            req = HttpRequest(
                method="POST",
                path="/telegram",
                query={},
                body={
                    "message": {
                        "chat": {"type": "group", "id": 123},
                        "text": "/tasks@dtm_bot",
                        "from": {"first_name": "Иван", "last_name": "Иванов"},
                    }
                },
                headers={},
                raw_event={},
                is_http_event=True,
            )

            response = asyncio.run(GroupQueryHandler(ctx).handle(req))
            self.assertIsNotNone(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(len(_FakeNotifier.sent), 1)
            self.assertEqual(_FakeNotifier.sent[0][0], 123)
            self.assertIn("Задача 1", _FakeNotifier.sent[0][1])
        finally:
            module.build_snapshot_engine = orig_build_snapshot_engine  # type: ignore[assignment]
            module.TelegramNotifier = orig_notifier  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()

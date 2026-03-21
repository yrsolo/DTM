from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

from src.platform.context import AppContext
from src.platform.runtime.commands.types import GROUP_QUERY_REPLY, UPDATE_SNAPSHOT
from src.entrypoints.http.dto import HttpRequest
from src.contexts.telegram_interaction.internal import TelegramWebhookHandler


class _FakeProducer:
    def __init__(self) -> None:
        self.commands = []

    def send(self, cmd) -> None:
        self.commands.append(cmd)


class _FakeStatusStore:
    def put_queued(self, cmd):
        return SimpleNamespace(requested_at_utc=cmd.created_at_utc)


def _ctx(producer=None, status_store=None) -> AppContext:
    cfg = SimpleNamespace(
        runtime=SimpleNamespace(
            telegram=SimpleNamespace(
                webhook_path="/telegram",
                allowed_updates=["message", "callback_query"],
                max_connections=5,
                secret_required=True,
            )
        )
    )
    deps = {
        "command_queue_producer": producer,
        "job_status_store": status_store,
        "tg_webhook_secret_token": "secret-123",
        "tg_bot_username": "@dtm_bot",
        "default_chat_id": "777",
    }
    return AppContext(cfg=cfg, deps=deps)


class TelegramWebhookHandlerTestCase(unittest.TestCase):
    def test_rejects_invalid_secret(self) -> None:
        response = TelegramWebhookHandler(_ctx()).handle(
            HttpRequest(
                method="POST",
                path="/telegram",
                headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
                body={"message": {"chat": {"type": "group", "id": 1}, "text": "/tasks@dtm_bot", "from": {"id": 2}}},
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 403)

    def test_enqueues_group_query_reply(self) -> None:
        producer = _FakeProducer()
        response = TelegramWebhookHandler(_ctx(producer=producer, status_store=_FakeStatusStore())).handle(
            HttpRequest(
                method="POST",
                path="/telegram",
                headers={"X-Telegram-Bot-Api-Secret-Token": "secret-123"},
                body={
                    "message": {
                        "chat": {"type": "group", "id": 123},
                        "text": "/tasks@dtm_bot",
                        "from": {"id": 2, "first_name": "Ð˜Ð²Ð°Ð½", "last_name": "Ð˜Ð²Ð°Ð½Ð¾Ð²"},
                    }
                },
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(len(producer.commands), 1)
        self.assertEqual(producer.commands[0].type, GROUP_QUERY_REPLY)
        payload = json.loads(response.body)
        self.assertEqual(payload["status"], "accepted")
        self.assertEqual(payload["command_name"], "group_tasks_me")

    def test_private_admin_update_command_enqueues_snapshot_update(self) -> None:
        producer = _FakeProducer()
        response = TelegramWebhookHandler(_ctx(producer=producer, status_store=_FakeStatusStore())).handle(
            HttpRequest(
                method="POST",
                path="/telegram",
                headers={"X-Telegram-Bot-Api-Secret-Token": "secret-123"},
                body={
                    "message": {
                        "chat": {"type": "private", "id": 777},
                        "text": "/update",
                        "from": {"id": 2, "first_name": "ÐÐ´Ð¼Ð¸Ð½"},
                    }
                },
                is_http_event=True,
            )
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(producer.commands[0].type, UPDATE_SNAPSHOT)
        payload = json.loads(response.body)
        self.assertEqual(payload["command_name"], "refresh_snapshot")


if __name__ == "__main__":
    unittest.main()


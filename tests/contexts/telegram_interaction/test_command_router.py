from __future__ import annotations

import unittest

from src.commands.types import GROUP_QUERY_REPLY, RENDER_TIMELINE_SHEET, SEND_REMINDERS, UPDATE_SNAPSHOT
from src.contexts.telegram_interaction.internal import (
    ParsedTelegramUpdate,
    TelegramCommandRouter,
    TelegramUpdateParser,
)


class TelegramParserAndRouterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = TelegramUpdateParser()
        self.router = TelegramCommandRouter()

    def test_parser_builds_typed_update_for_group_command(self) -> None:
        parsed = self.parser.parse(
            {
                "message": {
                    "chat": {"type": "group", "id": 123},
                    "text": "/tasks@dtm_bot",
                    "from": {"id": 2, "first_name": "Ivan", "last_name": "Ivanov"},
                }
            }
        )

        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.chat_type, "group")
        self.assertEqual(parsed.command, "/tasks")
        self.assertEqual(parsed.chat_id, "123")

    def test_router_maps_group_tasks_to_group_query_reply(self) -> None:
        parsed = ParsedTelegramUpdate(
            update_type="message",
            chat_id="123",
            chat_type="group",
            user_id="2",
            requester_name="Ivan Ivanov",
            text="/tasks@dtm_bot",
            command="/tasks",
            args="",
            raw={},
        )

        routed = self.router.route(parsed, bot_username="@dtm_bot", default_chat_id="777")

        self.assertIsNotNone(routed)
        assert routed is not None
        self.assertEqual(routed.command_type, GROUP_QUERY_REPLY)
        self.assertEqual(routed.command_name, "group_tasks_me")

    def test_router_maps_private_admin_commands(self) -> None:
        parsed = ParsedTelegramUpdate(
            update_type="message",
            chat_id="777",
            chat_type="private",
            user_id="2",
            requester_name="Admin",
            text="/update",
            command="/update",
            args="",
            raw={},
        )

        routed = self.router.route(parsed, bot_username="@dtm_bot", default_chat_id="777")

        self.assertEqual(routed.command_type, UPDATE_SNAPSHOT)
        self.assertEqual(routed.command_name, "refresh_snapshot")

        parsed = ParsedTelegramUpdate(
            update_type="message",
            chat_id="777",
            chat_type="private",
            user_id="2",
            requester_name="Admin",
            text="/send_statuses",
            command="/send_statuses",
            args="",
            raw={},
        )
        routed = self.router.route(parsed, bot_username="@dtm_bot", default_chat_id="777")
        self.assertEqual(routed.command_type, SEND_REMINDERS)

        parsed = ParsedTelegramUpdate(
            update_type="message",
            chat_id="777",
            chat_type="private",
            user_id="2",
            requester_name="Admin",
            text="/render_timeline",
            command="/render_timeline",
            args="",
            raw={},
        )
        routed = self.router.route(parsed, bot_username="@dtm_bot", default_chat_id="777")
        self.assertEqual(routed.command_type, RENDER_TIMELINE_SHEET)

    def test_parser_ignores_unsupported_update(self) -> None:
        parsed = self.parser.parse({"callback_query": {"id": "1"}})
        self.assertIsNone(parsed)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from src.platform.runtime.commands.types import GROUP_QUERY_REPLY, RENDER_TIMELINE_SHEET, SEND_REMINDERS, UPDATE_SNAPSHOT

from .model import ParsedTelegramUpdate, RoutedTelegramCommand

TASK_COMMANDS = frozenset({"/tasks", "/Ð·Ð°Ð´Ð°Ñ‡Ð¸"})
DEADLINE_COMMANDS = frozenset({"/deadlines", "/Ð´ÐµÐ´Ð»Ð°Ð¹Ð½Ñ‹"})
UPDATE_COMMANDS = frozenset({"/update", "/update_snapshot", "/refresh"})
TEST_REMINDER_COMMANDS = frozenset({"/reminders_test", "/notify_test", "/send_statuses"})
RENDER_COMMANDS = frozenset({"/render_timeline"})
DEADLINE_HINTS = ("Ð´ÐµÐ´Ð»Ð°Ð¹Ð½", "ÑÑ€Ð¾Ðº", "deadline")


class TelegramCommandRouter:
    @staticmethod
    def _bot_mention_matches(text: str, bot_username: str) -> bool:
        username = str(bot_username or "").strip().lstrip("@").lower()
        if not username:
            return False
        return f"@{username}" in str(text or "").lower()

    def route(self, parsed_update: ParsedTelegramUpdate, *, bot_username: str, default_chat_id: str = "") -> RoutedTelegramCommand | None:
        command = str(parsed_update.command or "").strip().lower()
        text_lower = str(parsed_update.text or "").lower()
        if parsed_update.chat_type in {"group", "supergroup"}:
            action = ""
            if command in TASK_COMMANDS:
                action = "tasks"
            elif command in DEADLINE_COMMANDS:
                action = "deadlines"
            elif self._bot_mention_matches(text_lower, bot_username):
                action = "deadlines" if any(token in text_lower for token in DEADLINE_HINTS) else "tasks"
            if not action:
                return None
            return RoutedTelegramCommand(
                command_name="group_deadlines_me" if action == "deadlines" else "group_tasks_me",
                command_type=GROUP_QUERY_REPLY,
                payload={"chat_id": parsed_update.chat_id, "requester_name": parsed_update.requester_name, "action": action, "statuses": ["work", "pre_done"], "include_today": True, "include_next_workday": True},
            )
        if parsed_update.chat_type == "private" and parsed_update.chat_id == str(default_chat_id or "").strip():
            if command in UPDATE_COMMANDS:
                return RoutedTelegramCommand(command_name="refresh_snapshot", command_type=UPDATE_SNAPSHOT, payload={"force_refresh": True, "dry_run": False})
            if command in TEST_REMINDER_COMMANDS:
                return RoutedTelegramCommand(command_name="send_statuses", command_type=SEND_REMINDERS, payload={"mode": "test", "statuses": ["work", "pre_done"], "include_today": True, "include_next_workday": True, "force_test_chat": True, "mock_external": False})
            if command in RENDER_COMMANDS:
                return RoutedTelegramCommand(command_name="render_timeline", command_type=RENDER_TIMELINE_SHEET, payload={"statuses": ["work", "pre_done"], "dry_run": False})
        return None


from __future__ import annotations

from src.app.context import AppContext
from src.contexts.telegram_interaction.public import (
    get_group_query_formatter as _get_group_query_formatter,
    get_snapshot_engine as _get_group_query_snapshot_engine,
    get_usecase as _get_group_query_usecase,
)
from src.notify import ReminderRequest
from src.telegram.sender import TelegramSender
from src.snapshot_engine import build_snapshot_engine


build_snapshot_engine = _get_group_query_snapshot_engine
TelegramSender = TelegramSender


class GroupQueryReplyJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    async def run(self, cmd):
        snapshot_engine = build_snapshot_engine(self._ctx)
        usecase = _get_group_query_usecase(snapshot_engine)
        groups, today, next_workday = usecase.select(
            ReminderRequest(
                mode="group_query",
                statuses=list(cmd.payload.get("statuses", ["work", "pre_done"])),
                include_today=bool(cmd.payload.get("include_today", True)),
                include_next_workday=bool(cmd.payload.get("include_next_workday", True)),
            )
        )
        formatter = _get_group_query_formatter()
        action = str(cmd.payload.get("action", "tasks")).strip().lower() or "tasks"
        requester_name = str(cmd.payload.get("requester_name", "")).strip()
        if action == "deadlines":
            reply = formatter.build_deadlines_reply(groups, today=today, next_workday=next_workday)
        else:
            reply = formatter.build_tasks_reply(
                groups,
                requester_name=requester_name,
                today=today,
                next_workday=next_workday,
            )
        sender = TelegramSender(
            bot_token=str(self._ctx.deps.get("tg_bot_token", "")),
            default_chat_id=self._ctx.deps.get("default_chat_id"),
        )
        await sender.send_message(cmd.payload.get("chat_id"), reply, parse_mode=None)
        return {
            "artifact": "group_query_reply",
            "status": "ok",
            "action": action,
            "chat_id": str(cmd.payload.get("chat_id", "")),
            "requester_name": requester_name,
            "message_length": len(reply),
        }

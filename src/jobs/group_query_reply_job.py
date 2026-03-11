from __future__ import annotations

from src.app.context import AppContext
from src.notify import GroupQueryFormatter, ReminderRequest, ReminderUseCase
from src.snapshot_engine import build_snapshot_engine
from src.telegram.sender import TelegramSender


class GroupQueryReplyJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    async def run(self, cmd):
        snapshot_engine = build_snapshot_engine(self._ctx)
        usecase = ReminderUseCase(snapshot_engine)
        groups, today, next_workday = usecase.select(
            ReminderRequest(
                mode="group_query",
                statuses=list(cmd.payload.get("statuses", ["work", "pre_done"])),
                include_today=bool(cmd.payload.get("include_today", True)),
                include_next_workday=bool(cmd.payload.get("include_next_workday", True)),
            )
        )
        formatter = GroupQueryFormatter()
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

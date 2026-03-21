from __future__ import annotations

from src.app.context import AppContext
from src.contexts.telegram_interaction.public import (
    get_group_query_formatter as _get_group_query_formatter,
    get_sender as _get_group_query_sender,
    get_snapshot_read_api as _get_group_query_snapshot_read_api,
    get_usecase as _get_group_query_usecase,
    make_group_query_request as _make_group_query_request_from_module,
)


get_snapshot_read_api = _get_group_query_snapshot_read_api


def _make_group_query_request(**kwargs):
    return _make_group_query_request_from_module(**kwargs)


def _make_group_query_sender(ctx: AppContext):
    return _get_group_query_sender(ctx)


class GroupQueryReplyJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    async def run(self, cmd):
        snapshot_read = get_snapshot_read_api(self._ctx)
        usecase = _get_group_query_usecase(snapshot_read)
        groups, today, next_workday = usecase.select(
            _make_group_query_request(
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
        sender = _make_group_query_sender(self._ctx)
        await sender.send_message(cmd.payload.get("chat_id"), reply, parse_mode=None)
        return {
            "artifact": "group_query_reply",
            "status": "ok",
            "action": action,
            "chat_id": str(cmd.payload.get("chat_id", "")),
            "requester_name": requester_name,
            "message_length": len(reply),
        }


__all__ = ["GroupQueryReplyJob"]

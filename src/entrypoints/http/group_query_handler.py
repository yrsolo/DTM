"""Group-query HTTP handler."""

from __future__ import annotations

from typing import Any

from src.adapters.telegram import TelegramNotifier
from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.group_query_tasks_loader import load_work_tasks_for_group_query
from src.entrypoints.http.response_utils import json_response
from src.legacy.http_core_bindings import build_deadlines_reply, build_tasks_reply, parse_group_query_request


class GroupQueryHandler:
    """Telegram group query webhook handler."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None

        deps = self._ctx.deps
        bot_username = str(deps.get("tg_bot_username", ""))
        query = parse_group_query_request(req.body, bot_username=bot_username)
        if query is None:
            return None

        notifier = TelegramNotifier(
            bot_token=str(deps.get("tg_bot_token", "")),
            default_chat_id=deps.get("default_chat_id"),
        )
        try:
            tasks = load_work_tasks_for_group_query(
                key_json=str(deps.get("key_json", "")),
                sheet_info=dict(deps.get("sheet_info", {})),
                app_cfg=self._ctx.cfg,
            )
            if query.action == "deadlines":
                reply = build_deadlines_reply(tasks)
            else:
                reply = build_tasks_reply(tasks, requester_name=query.requester_name)
            await notifier.send_message(query.chat_id, reply, parse_mode=None)
            return json_response(200, {"artifact": "group_query", "status": "ok"})
        except Exception as error:
            print(f"group_query_error={error}")
            await notifier.send_message(
                query.chat_id,
                "?? ?????? ??????? ?????? ?????. ?????????? ??? ??? ????? ??????.",
                parse_mode=None,
            )
            return json_response(200, {"artifact": "group_query", "status": "error"})

"""Yandex Cloud entrypoint with planner and group-query handling."""

from __future__ import annotations

import json
import traceback
from typing import Any

from config import KEY_JSON, SHEET_INFO, TG_BOT_USERNAME
from core.bootstrap import build_planner_dependencies
from core.group_query import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)
from core.reminder import TelegramNotifier
from main import main


def _extract_payload(event: Any) -> tuple[dict[str, Any], bool]:
    if not isinstance(event, dict):
        return {}, False
    if "body" not in event:
        return event, False

    raw_body = event.get("body")
    if isinstance(raw_body, dict):
        return raw_body, True
    if isinstance(raw_body, str) and raw_body.strip():
        try:
            parsed = json.loads(raw_body)
            if isinstance(parsed, dict):
                return parsed, True
        except json.JSONDecodeError:
            pass
    return {}, True


def _load_work_tasks_for_group_query() -> list[Any]:
    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=True,
        mock_external=True,
    )
    return dependencies.task_repository.get_task_by_color_status(["work", "pre_done"])


async def _handle_group_query_if_requested(request_payload: dict[str, Any], is_http_event: bool) -> bool:
    if not is_http_event:
        return False

    query = parse_group_query_request(request_payload, bot_username=TG_BOT_USERNAME)
    if query is None:
        return False

    notifier = TelegramNotifier()
    try:
        tasks = _load_work_tasks_for_group_query()
        if query.action == "deadlines":
            reply = build_deadlines_reply(tasks)
        else:
            reply = build_tasks_reply(tasks, requester_name=query.requester_name)
        await notifier.send_message(query.chat_id, reply, parse_mode=None)
        return True
    except Exception as error:
        print(f"group_query_error={error}")
        await notifier.send_message(
            query.chat_id,
            "Не смогла собрать список задач. Попробуйте еще раз через минуту.",
            parse_mode=None,
        )
        return True


async def handler(event: Any, _: Any) -> dict[str, Any]:
    """Yandex Cloud handler."""
    request_payload, is_http_event = _extract_payload(event)
    if request_payload.get("healthcheck"):
        return {
            "statusCode": 200,
            "body": "!HEALTHY!",
        }

    if await _handle_group_query_if_requested(request_payload, is_http_event):
        return {
            "statusCode": 200,
            "body": "!GROUP_QUERY_OK!",
        }

    run_mode = request_payload.get("mode")
    dry_run = bool(request_payload.get("dry_run", False))
    mock_external = request_payload.get("mock_external")
    planner_event = request_payload.get("event")
    if planner_event is None and not is_http_event:
        planner_event = event

    try:
        await main(
            event=planner_event,
            mode=run_mode,
            dry_run=dry_run,
            mock_external=mock_external,
        )
    except Exception as ex:
        tr = str(traceback.format_exc())
        txt = f"Runtime failure:\n{ex}\nTRACEBACK\n{tr}\n"

        print(txt)
        try:
            await TelegramNotifier().alog(txt)
        except Exception as notifier_error:
            print(f"Error notifier failed: {notifier_error}")

        return {
            "statusCode": 200,
            "body": "!!!EGGORR!!!",
        }

    return {
        "statusCode": 200,
        "body": "!GOOD!",
    }

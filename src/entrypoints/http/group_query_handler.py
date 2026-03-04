"""Group-query HTTP handler extracted from index entrypoint."""

from __future__ import annotations

from typing import Any, Callable


async def handle_group_query_if_requested(
    request_payload: dict[str, Any],
    is_http_event: bool,
    *,
    bot_username: str,
    parse_group_query_request: Callable[..., Any],
    notifier_factory: Callable[[], Any],
    load_work_tasks_for_group_query: Callable[[], list[Any]],
    build_deadlines_reply: Callable[[list[Any]], str],
    build_tasks_reply: Callable[[list[Any], str | None], str],
) -> bool:
    if not is_http_event:
        return False

    query = parse_group_query_request(request_payload, bot_username=bot_username)
    if query is None:
        return False

    notifier = notifier_factory()
    try:
        tasks = load_work_tasks_for_group_query()
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
            "\u041d\u0435 \u0441\u043c\u043e\u0433\u043b\u0430 \u0441\u043e\u0431\u0440\u0430\u0442\u044c "
            "\u0441\u043f\u0438\u0441\u043e\u043a \u0437\u0430\u0434\u0430\u0447. "
            "\u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0435\u0449\u0435 "
            "\u0440\u0430\u0437 \u0447\u0435\u0440\u0435\u0437 \u043c\u0438\u043d\u0443\u0442\u0443.",
            parse_mode=None,
        )
        return True

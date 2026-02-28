"""Smoke check for Telegram group query parsing and rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from core.group_query import (
    build_deadlines_reply,
    build_tasks_reply,
    parse_group_query_request,
)


@dataclass
class FakeTask:
    name: str
    designer: str
    timing: dict[pd.Timestamp, list[str]]
    max_date: pd.Timestamp


def _build_fake_tasks(today: pd.Timestamp) -> list[FakeTask]:
    task_a_date = today + pd.Timedelta(days=1)
    task_b_date = today + pd.Timedelta(days=2)
    return [
        FakeTask(
            name="Бренд А [Проект] Формат",
            designer="Иван Иванов",
            timing={task_a_date: ["этап 1"]},
            max_date=task_a_date,
        ),
        FakeTask(
            name="Бренд Б [Проект] Формат",
            designer="Петр Петров",
            timing={task_b_date: ["этап 2"]},
            max_date=task_b_date,
        ),
    ]


def _assert_parsing() -> None:
    update = {
        "message": {
            "chat": {"id": -1001, "type": "supergroup"},
            "from": {"first_name": "Иван", "last_name": "Иванов"},
            "text": "/tasks@dtm_bot",
        }
    }
    request = parse_group_query_request(update, bot_username="dtm_bot")
    assert request is not None
    assert request.action == "tasks"
    assert request.chat_id == -1001
    assert request.requester_name == "Иван Иванов"

    mention_update = {
        "message": {
            "chat": {"id": -1001, "type": "group"},
            "from": {"first_name": "Иван", "last_name": "Иванов"},
            "text": "@dtm_bot покажи дедлайны",
        }
    }
    mention_request = parse_group_query_request(mention_update, bot_username="dtm_bot")
    assert mention_request is not None
    assert mention_request.action == "deadlines"


def _assert_rendering() -> None:
    today = pd.Timestamp("2026-02-28")
    tasks = _build_fake_tasks(today)
    personal = build_tasks_reply(tasks, requester_name="Иван Иванов", today=today)
    assert "ваши ближайшие задачи" in personal.lower()
    assert "Бренд А" in personal
    assert "Бренд Б" not in personal

    deadlines = build_deadlines_reply(tasks, today=today)
    assert "Ближайшие дедлайны" in deadlines
    assert "Бренд А" in deadlines and "Бренд Б" in deadlines


def main() -> None:
    _assert_parsing()
    _assert_rendering()
    print("group_query_smoke_ok")


if __name__ == "__main__":
    main()

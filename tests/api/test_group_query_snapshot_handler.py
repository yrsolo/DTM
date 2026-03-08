from __future__ import annotations

import asyncio
import unittest
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.group_query_handler import GroupQueryHandler
from src.notify.usecase import next_workday
from src.snapshot_engine.model import Milestone, PrepIndexes, PrepSnapshot, TaskSheet, TaskView


class _FakeNotifier:
    sent: list[tuple[int | str, str, str | None]] = []

    def __init__(self, bot_token=None, default_chat_id=None) -> None:  # noqa: ANN001, D401
        _ = bot_token, default_chat_id

    async def send_message(self, chat_id, text, parse_mode=None):  # noqa: ANN001
        self.sent.append((chat_id, text, parse_mode))
        return None


class _FakeSnapshotEngine:
    def __init__(self, prep: PrepSnapshot) -> None:
        self._prep = prep

    def get_prep_snapshot(self) -> PrepSnapshot:
        return self._prep


def _task(task_id: str, owner: str, milestone_day: date, *, title: str) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=title,
            owner_id=owner,
            group_id="project",
            brand="brand",
            format_="format",
            customer="customer",
            raw_timing="raw",
            status="work",
            history="history",
            timing={milestone_day.isoformat(): ["финал"]},
            milestones=[Milestone(type="финал", planned=milestone_day)],
        ),
        extra=None,
    )


class GroupQuerySnapshotHandlerTestCase(unittest.TestCase):
    def test_tasks_query_uses_shared_reminder_selection(self) -> None:
        import src.entrypoints.http.group_query_handler as module

        orig_build_snapshot_engine = module.build_snapshot_engine
        orig_notifier = module.TelegramNotifier
        try:
            today = date.today()
            far_future = next_workday(today) + timedelta(days=7)
            prep = PrepSnapshot(
                source_id="sheet:test",
                raw_source_hash="hash",
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id={
                    "t1": _task("t1", "Иван Иванов", today, title="Задача сегодня"),
                    "t2": _task("t2", "Петр Петров", today, title="Чужая задача"),
                    "t3": _task("t3", "Иван Иванов", far_future, title="Далёкая задача"),
                },
                indexes=PrepIndexes(),
            )
            module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine(prep)  # type: ignore[assignment]
            module.TelegramNotifier = _FakeNotifier  # type: ignore[assignment]
            _FakeNotifier.sent = []

            ctx = AppContext(
                cfg=SimpleNamespace(),
                deps={"tg_bot_username": "@dtm_bot", "tg_bot_token": "x", "default_chat_id": "0"},
            )
            req = HttpRequest(
                method="POST",
                path="/telegram",
                query={},
                body={
                    "message": {
                        "chat": {"type": "group", "id": 123},
                        "text": "/tasks@dtm_bot",
                        "from": {"first_name": "Иван", "last_name": "Иванов"},
                    }
                },
                headers={},
                raw_event={},
                is_http_event=True,
            )

            response = asyncio.run(GroupQueryHandler(ctx).handle(req))
            self.assertIsNotNone(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(len(_FakeNotifier.sent), 1)
            self.assertEqual(_FakeNotifier.sent[0][0], 123)
            self.assertIn("Задача сегодня", _FakeNotifier.sent[0][1])
            self.assertNotIn("Чужая задача", _FakeNotifier.sent[0][1])
            self.assertNotIn("Далёкая задача", _FakeNotifier.sent[0][1])
        finally:
            module.build_snapshot_engine = orig_build_snapshot_engine  # type: ignore[assignment]
            module.TelegramNotifier = orig_notifier  # type: ignore[assignment]

    def test_deadlines_query_returns_team_preview_for_today_and_next_workday(self) -> None:
        import src.entrypoints.http.group_query_handler as module

        orig_build_snapshot_engine = module.build_snapshot_engine
        orig_notifier = module.TelegramNotifier
        try:
            today = date.today()
            next_day = next_workday(today)
            prep = PrepSnapshot(
                source_id="sheet:test",
                raw_source_hash="hash",
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id={
                    "t1": _task("t1", "Иван Иванов", today, title="Сегодняшняя"),
                    "t2": _task("t2", "Петр Петров", next_day, title="Завтрашняя"),
                    "t3": _task("t3", "Петр Петров", next_day, title="Ещё одна"),
                },
                indexes=PrepIndexes(),
            )
            module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine(prep)  # type: ignore[assignment]
            module.TelegramNotifier = _FakeNotifier  # type: ignore[assignment]
            _FakeNotifier.sent = []

            ctx = AppContext(
                cfg=SimpleNamespace(),
                deps={"tg_bot_username": "@dtm_bot", "tg_bot_token": "x", "default_chat_id": "0"},
            )
            req = HttpRequest(
                method="POST",
                path="/telegram",
                query={},
                body={
                    "message": {
                        "chat": {"type": "group", "id": 555},
                        "text": "/deadlines@dtm_bot",
                        "from": {"first_name": "Иван", "last_name": "Иванов"},
                    }
                },
                headers={},
                raw_event={},
                is_http_event=True,
            )

            response = asyncio.run(GroupQueryHandler(ctx).handle(req))
            self.assertIsNotNone(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(len(_FakeNotifier.sent), 1)
            self.assertIn("Сегодняшняя", _FakeNotifier.sent[0][1])
            self.assertIn("Завтрашняя", _FakeNotifier.sent[0][1])
            self.assertIn("Петр Петров", _FakeNotifier.sent[0][1])
        finally:
            module.build_snapshot_engine = orig_build_snapshot_engine  # type: ignore[assignment]
            module.TelegramNotifier = orig_notifier  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()

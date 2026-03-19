from __future__ import annotations

import asyncio
import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

from src.app.context import AppContext
from src.commands.model import Command, RequestedBy
from src.jobs.group_query_reply_job import GroupQueryReplyJob
from src.notify.usecase import next_workday
from src.snapshot_engine.model import Milestone, PrepIndexes, PrepSnapshot, TaskSheet, TaskView


class _FakeSnapshotEngine:
    def __init__(self, prep: PrepSnapshot):
        self._prep = prep

    def get_prep_snapshot(self) -> PrepSnapshot:
        return self._prep


class _FakeSender:
    def __init__(self, bot_token=None, default_chat_id=None) -> None:  # noqa: ANN001
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.sent: list[tuple[str | int, str, str | None]] = []

    async def send_message(self, chat_id, text, parse_mode=None):  # noqa: ANN001
        self.sent.append((chat_id, text, parse_mode))
        return None


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


class GroupQueryReplyJobTestCase(unittest.TestCase):
    def test_group_query_reply_job_sends_selected_tasks(self) -> None:
        import src.jobs.group_query_reply_job as module

        orig_build_snapshot_engine = module.build_snapshot_engine
        orig_build_sender = module._build_group_query_sender
        try:
            today = date.today()
            prep = PrepSnapshot(
                source_id="sheet:test",
                raw_source_hash="hash",
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id={
                    "1": _task("1", "Иван Иванов", today, title="Сегодняшняя задача"),
                    "2": _task("2", "Петр Петров", next_workday(today), title="Чужая задача"),
                },
                indexes=PrepIndexes(),
            )
            sender = _FakeSender()
            module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine(prep)  # type: ignore[assignment]
            module._build_group_query_sender = lambda _ctx: sender  # type: ignore[assignment]

            ctx = AppContext(cfg=SimpleNamespace(), deps={"tg_bot_token": "x", "default_chat_id": "0"})
            cmd = Command(
                job_id="job-1",
                type="group_query_reply",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="telegram", user_id="2", chat_id="123"),
                payload={"chat_id": "123", "requester_name": "Иван Иванов", "action": "tasks"},
            )

            result = asyncio.run(GroupQueryReplyJob(ctx).run(cmd))
            self.assertEqual(result["status"], "ok")
            self.assertEqual(len(sender.sent), 1)
            self.assertIn("Сегодняшняя задача", sender.sent[0][1])
            self.assertNotIn("Чужая задача", sender.sent[0][1])
        finally:
            module.build_snapshot_engine = orig_build_snapshot_engine  # type: ignore[assignment]
            module._build_group_query_sender = orig_build_sender  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()

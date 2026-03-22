from __future__ import annotations

import asyncio
import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

from src.platform.context import AppContext
from src.platform.runtime.commands.model import Command, RequestedBy
from src.contexts.telegram_interaction.internal.job_runner import GroupQueryReplyJob
from src.contexts.reminders.internal import next_workday
from src.contexts.snapshot.internal.engine.model import Milestone, PrepIndexes, PrepSnapshot, TaskSheet, TaskView


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


class _FakeInteractionApi:
    def __init__(self, *, prep: PrepSnapshot, sender: _FakeSender) -> None:
        self._snapshot_read = _FakeSnapshotEngine(prep)
        self._sender = sender

    def snapshot_read_api(self):
        return self._snapshot_read

    def usecase(self, snapshot_read):  # noqa: ANN001
        from src.contexts.telegram_interaction.internal.group_query_usecase import GroupQueryUseCase

        return GroupQueryUseCase(snapshot_read)

    def group_query_formatter(self):
        from src.contexts.telegram_interaction.internal.group_query_formatter import GroupQueryFormatter

        return GroupQueryFormatter()

    def sender(self):
        return self._sender

    def request(self, **kwargs):  # noqa: ANN003
        from src.contexts.telegram_interaction.internal.group_query_request import GroupQueryRequest

        return GroupQueryRequest(**kwargs)


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
            timing={milestone_day.isoformat(): ["Ñ„Ð¸Ð½Ð°Ð»"]},
            milestones=[Milestone(type="Ñ„Ð¸Ð½Ð°Ð»", planned=milestone_day)],
        ),
        extra=None,
    )


class GroupQueryReplyJobTestCase(unittest.TestCase):
    def test_group_query_reply_job_sends_selected_tasks(self) -> None:
        import src.contexts.telegram_interaction.internal.job_runner as module

        orig_get_interaction_api = module.get_interaction_api
        try:
            today = date.today()
            prep = PrepSnapshot(
                source_id="sheet:test",
                raw_source_hash="hash",
                built_at_utc=datetime.now(timezone.utc),
                tasks_by_id={
                    "1": _task("1", "Ð˜Ð²Ð°Ð½ Ð˜Ð²Ð°Ð½Ð¾Ð²", today, title="Ð¡ÐµÐ³Ð¾Ð´Ð½ÑÑˆÐ½ÑÑ Ð·Ð°Ð´Ð°Ñ‡Ð°"),
                    "2": _task("2", "ÐŸÐµÑ‚Ñ€ ÐŸÐµÑ‚Ñ€Ð¾Ð²", next_workday(today), title="Ð§ÑƒÐ¶Ð°Ñ Ð·Ð°Ð´Ð°Ñ‡Ð°"),
                },
                indexes=PrepIndexes(),
            )
            sender = _FakeSender()
            module.get_interaction_api = lambda _ctx: _FakeInteractionApi(prep=prep, sender=sender)  # type: ignore[assignment]

            ctx = AppContext(cfg=SimpleNamespace(), deps={"tg_bot_token": "x", "default_chat_id": "0"})
            cmd = Command(
                job_id="job-1",
                type="group_query_reply",
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="telegram", user_id="2", chat_id="123"),
                payload={"chat_id": "123", "requester_name": "Ð˜Ð²Ð°Ð½ Ð˜Ð²Ð°Ð½Ð¾Ð²", "action": "tasks"},
            )

            result = asyncio.run(GroupQueryReplyJob(ctx).run(cmd))
            self.assertEqual(result["status"], "ok")
            self.assertEqual(len(sender.sent), 1)
            self.assertIn("Ð¡ÐµÐ³Ð¾Ð´Ð½ÑÑˆÐ½ÑÑ Ð·Ð°Ð´Ð°Ñ‡Ð°", sender.sent[0][1])
            self.assertNotIn("Ð§ÑƒÐ¶Ð°Ñ Ð·Ð°Ð´Ð°Ñ‡Ð°", sender.sent[0][1])
        finally:
            module.get_interaction_api = orig_get_interaction_api  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()



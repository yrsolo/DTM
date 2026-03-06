from __future__ import annotations

import asyncio
import unittest
from datetime import datetime, timezone

from src.notify import ReminderFormatter, ReminderJob, ReminderRequest, ReminderUseCase, TelegramReminderSender
from src.snapshot_engine.model import PrepIndexes, PrepSnapshot, TaskSheet, TaskView, Window


class _FakeEngine:
    def __init__(self, prep: PrepSnapshot | None) -> None:
        self._prep = prep

    def get_prep_snapshot(self) -> PrepSnapshot | None:
        return self._prep


class _FakeTelegram:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send_message(self, chat_id: str, text: str):  # noqa: ANN201
        self.sent.append((chat_id, text))
        return {"ok": True}


def _task(task_id: str, owner: str, status: str, day: str) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=f"title-{task_id}",
            owner_id=owner,
            group_id="g",
            brand="b",
            format_="f",
            customer="c",
            raw_timing="raw",
            status=status,
            history=f"h-{task_id}",
            timing={day: ["stage"]},
            milestones=[],
        ),
        extra=None,
    )


class ReminderV2TestCase(unittest.TestCase):
    def test_usecase_filters_active_statuses(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "1": _task("1", "Alice", "work", "2026-03-10"),
                "2": _task("2", "Alice", "done", "2026-03-10"),
                "3": _task("3", "Bob", "pre_done", "2026-03-10"),
            },
            indexes=PrepIndexes(),
        )
        usecase = ReminderUseCase(_FakeEngine(prep))
        result = usecase.run(
            ReminderRequest(
                window=Window(start=None, end=None),
                statuses=["work", "pre_done"],
            )
        )
        owners = [item.owner_id for item in result.groups]
        self.assertEqual(owners, ["Alice", "Bob"])
        self.assertEqual(sum(len(item.tasks) for item in result.groups), 2)

    def test_job_sends_to_default_chat_when_owner_is_not_chat_id(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task("1", "Alice", "work", "2026-03-10")},
            indexes=PrepIndexes(),
        )
        usecase = ReminderUseCase(_FakeEngine(prep))
        formatter = ReminderFormatter()
        fake_tg = _FakeTelegram()
        sender = TelegramReminderSender(fake_tg, default_chat_id="-100123")
        job = ReminderJob(usecase, formatter, sender)
        asyncio.run(
            job.run(
                ReminderRequest(
                    window=Window(start=None, end=None),
                    statuses=["work"],
                )
            )
        )
        self.assertEqual(len(fake_tg.sent), 1)
        self.assertEqual(fake_tg.sent[0][0], "-100123")
        self.assertIn("h-1", fake_tg.sent[0][1])

    def test_formatter_renders_group_header_and_task_line(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={"1": _task("1", "Alice", "work", "2026-03-10")},
            indexes=PrepIndexes(),
        )
        usecase = ReminderUseCase(_FakeEngine(prep))
        result = usecase.run(
            ReminderRequest(
                window=Window(start=None, end=None),
                statuses=["work"],
            )
        )
        message = ReminderFormatter().format(result)[0]
        self.assertIn("Напоминания: Alice", message.text)
        self.assertIn("title-1", message.text)
        self.assertIn("[work]", message.text)


if __name__ == "__main__":
    unittest.main()

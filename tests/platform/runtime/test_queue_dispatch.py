from __future__ import annotations

import asyncio
import unittest
from datetime import datetime, timezone

from src.platform.runtime.commands.model import Command, RequestedBy
from src.platform.runtime.queue_dispatch import dispatch_command


class _FakeJob:
    def __init__(self, artifact: str) -> None:
        self.artifact = artifact
        self.called = 0

    def run(self, _command: Command) -> dict[str, object]:
        self.called += 1
        return {"artifact": self.artifact, "status": "ok"}


def _command(command_type: str) -> Command:
    return Command(
        job_id="job-1",
        type=command_type,
        created_at_utc=datetime(2026, 3, 19, 12, 0, tzinfo=timezone.utc),
        requested_by=RequestedBy(source="test"),
    )


class QueueDispatchTestCase(unittest.TestCase):
    def test_known_command_routes_to_attachments_owner(self) -> None:
        attachments_job = _FakeJob("attach_task_file")
        result = asyncio.run(
            dispatch_command(
                _command("attach_task_file"),
                command_handlers={
                    "update_snapshot": _FakeJob("update_snapshot"),
                    "send_reminders": _FakeJob("send_reminders"),
                    "render_timeline_sheet": _FakeJob("render_timeline"),
                    "render_designers_sheet": _FakeJob("render_designers"),
                    "group_query_reply": _FakeJob("group_query_reply"),
                    "attach_task_file": attachments_job,
                    "delete_task_attachment": _FakeJob("delete_task_attachment"),
                    "cleanup_task_attachments": _FakeJob("cleanup_task_attachments"),
                    "generate_attachment_preview": _FakeJob("generate_attachment_preview"),
                },
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(attachments_job.called, 1)

    def test_unknown_command_is_terminal(self) -> None:
        result = asyncio.run(
            dispatch_command(
                _command("unknown_command"),
                command_handlers={
                    "update_snapshot": _FakeJob("update_snapshot"),
                    "send_reminders": _FakeJob("send_reminders"),
                    "render_timeline_sheet": _FakeJob("render_timeline"),
                    "render_designers_sheet": _FakeJob("render_designers"),
                    "group_query_reply": _FakeJob("group_query_reply"),
                    "attach_task_file": _FakeJob("attach_task_file"),
                    "delete_task_attachment": _FakeJob("delete_task_attachment"),
                    "cleanup_task_attachments": _FakeJob("cleanup_task_attachments"),
                    "generate_attachment_preview": _FakeJob("generate_attachment_preview"),
                },
            )
        )

        self.assertFalse(result.success)
        self.assertFalse(result.retryable)
        self.assertEqual(result.error_code, "unsupported_command_type")


if __name__ == "__main__":
    unittest.main()


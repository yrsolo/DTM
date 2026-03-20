from __future__ import annotations

from typing import Any

from src.commands.model import Command
from src.platform.runtime.queue_dispatch import dispatch_command

from .model import JobResult


class CommandDispatcher:
    def __init__(
        self,
        update_snapshot_job: Any,
        send_reminders_job: Any,
        render_timeline_job: Any,
        render_designers_job: Any,
        group_query_reply_job: Any,
        attach_task_file_job: Any,
        delete_task_attachment_job: Any,
        cleanup_task_attachments_job: Any,
        generate_attachment_preview_job: Any,
    ) -> None:
        self._update_snapshot_job = update_snapshot_job
        self._send_reminders_job = send_reminders_job
        self._render_timeline_job = render_timeline_job
        self._render_designers_job = render_designers_job
        self._group_query_reply_job = group_query_reply_job
        self._attach_task_file_job = attach_task_file_job
        self._delete_task_attachment_job = delete_task_attachment_job
        self._cleanup_task_attachments_job = cleanup_task_attachments_job
        self._generate_attachment_preview_job = generate_attachment_preview_job

    async def dispatch(self, cmd: Command) -> JobResult:
        return await dispatch_command(
            cmd,
            update_snapshot_job=self._update_snapshot_job,
            send_reminders_job=self._send_reminders_job,
            render_timeline_job=self._render_timeline_job,
            render_designers_job=self._render_designers_job,
            group_query_reply_job=self._group_query_reply_job,
            attach_task_file_job=self._attach_task_file_job,
            delete_task_attachment_job=self._delete_task_attachment_job,
            cleanup_task_attachments_job=self._cleanup_task_attachments_job,
            generate_attachment_preview_job=self._generate_attachment_preview_job,
        )

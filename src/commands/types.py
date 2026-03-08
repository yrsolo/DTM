from __future__ import annotations

UPDATE_SNAPSHOT = "update_snapshot"
SEND_REMINDERS = "send_reminders"
RENDER_TIMELINE_SHEET = "render_timeline_sheet"
RENDER_DESIGNERS_SHEET = "render_designers_sheet"
GROUP_QUERY_REPLY = "group_query_reply"
ATTACH_TASK_FILE = "attach_task_file"

SUPPORTED_COMMAND_TYPES = frozenset(
    {
        UPDATE_SNAPSHOT,
        SEND_REMINDERS,
        RENDER_TIMELINE_SHEET,
        RENDER_DESIGNERS_SHEET,
        GROUP_QUERY_REPLY,
        ATTACH_TASK_FILE,
    }
)

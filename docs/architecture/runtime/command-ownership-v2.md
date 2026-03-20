# Command Ownership V2

This document defines the target ownership of async command types for the modular-monolith refactor wave.

Governing source:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Command ownership

| Command type | Owning context | Runtime intake | Expected side effects |
|---|---|---|---|
| `update_snapshot` | `snapshot` | queue worker | refresh prepared snapshot/state |
| `render_timeline_sheet` | `rendering` | queue worker | regenerate timeline representation and write it out |
| `render_designers_sheet` | `rendering` | queue worker | regenerate designers representation and write it out |
| `send_reminders` | `reminders` | queue worker | select reminder candidates and deliver reminders |
| `group_query_reply` | `telegram_interaction` | queue worker | build and send group-query Telegram response |
| `attach_task_file` | `attachments` | queue worker | finalize publication of file metadata and preview follow-up |
| `delete_task_attachment` | `attachments` | queue worker | delete/retire attachment from published state and storage lifecycle |
| `cleanup_task_attachments` | `attachments` | queue worker | cleanup stale attachment lifecycle state |
| `generate_attachment_preview` | `attachments` | queue worker | generate or finalize preview artifact lifecycle |

## Rules

- queue routing must be explicit via `match/case`
- worker/runtime may parse and dispatch commands, but ownership belongs to the listed context
- command handlers may delegate to local module internals, but the ownership map above is the canonical target
- no command should stay owned by generic `worker` or `jobs` as a conceptual home

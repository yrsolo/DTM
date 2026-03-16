# Telegram Command Matrix

| User action | Context | Internal command name | Internal command type | Execution mode |
|---|---|---|---|---|
| `/tasks` or bot mention asking tasks | group/supergroup | `group_tasks_me` | `group_query_reply` | async |
| `/deadlines` or bot mention asking deadlines | group/supergroup | `group_deadlines_me` | `group_query_reply` | async |
| `/update` from default admin chat | private | `refresh_snapshot` | `update_snapshot` | async |
| `/send_statuses` from default admin chat | private | `send_statuses` | `send_reminders` | async |
| `/render_timeline` from default admin chat | private | `render_timeline` | `render_timeline_sheet` | async |

## Notes

- parser builds a typed `ParsedTelegramUpdate`
- router maps parsed DTO to internal command intent
- webhook remains enqueue-only
- group query continues to use reminder selection path on worker side

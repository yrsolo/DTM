# Stage 17 Group Query Runtime

## Delivered behavior
- Added group query parsing and rendering module:
  - `core/group_query.py`
- Added cloud runtime route in `index.py`:
  - For Telegram HTTP updates in `group/supergroup`, parse command/mention.
  - Build task/deadline response from current repository snapshot.
  - Send response to same chat via `TelegramNotifier`.
  - Return early without running planner pipeline.

## Supported interactions
- Commands:
  - `/tasks`, `/tasks@<bot>`
  - `/deadlines`, `/deadlines@<bot>`
  - Russian aliases: `/задачи`, `/дедлайны`
- Mention mode:
  - `@<bot_username> ... задачи`
  - `@<bot_username> ... дедлайны`

## Environment
- `TG_BOT_USERNAME` controls mention parsing (`@<bot_username>`).

## Response format
- `tasks` action:
  - Shows requester's nearest tasks by due date.
- `deadlines` action:
  - Shows nearest deadlines across active team tasks.

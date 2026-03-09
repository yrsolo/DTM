# Runtime Modes (Current)

## Supported standard modes

### `timer`
- canonical scheduled mode
- updates snapshot storage
- may trigger render/notify flows depending on caller path, but standard timer runtime is snapshot-first

### `sync-only`
- explicit rebuild mode
- updates raw/prep snapshots
- used for manual refresh and local/test smoke

### `render_v2`
- renders Google Sheets views from Prep snapshot
- supported targets:
  - timeline sheet (`Задачи`)
  - designers sheet (`Дизайнеры`)

### `reminder_v2`
- sends reminder flow through new notify contour

### `reminders-only`
- reminder-only execution without sync/update

### `morning`
- production-like reminder mode for workday delivery

### `test`
- safe operator/developer mode
- test-chat routing for reminders
- safe defaults for mocks where configured

## Transport mapping
- HTTP explicit runtime requests go through:
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/runtime/runtime_shell.py`
- scheduled triggers go through:
  - `src/entrypoints/triggers/trigger_shell.py`
- queue worker jobs bypass ad-hoc mode routing and execute explicit command jobs

## Unsupported legacy modes
Legacy planner/store modes are not part of the standard runtime anymore.

Behavior:
- HTTP: explicit unsupported response
- runtime shell/debug: structured `unsupported_mode`

## Timezone policy
- human-facing render timestamps use `runtime.timezone` (default `Europe/Moscow`)
- JSON/system timestamps remain UTC ISO

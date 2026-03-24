# Режимы runtime

## Поддерживаемые режимы

### `timer`
- основной scheduled mode;
- обновляет snapshot storage;
- может запускать render/reminder-related flows через канонический runtime contour.

### `sync-only`
- явный rebuild mode;
- обновляет raw/prep snapshots;
- используется для manual refresh и local/test smoke.

### `render_v2`
- рендерит Google Sheets views из prep snapshot;
- поддерживает:
  - timeline sheet (`Задачи`)
  - designers sheet (`Дизайнеры`)

### `reminder_v2`
- запускает reminder flow через текущий reminder contour.

### `reminders-only`
- выполняет только reminder delivery без sync/update.

### `morning`
- platform-owned утренний orchestration slot;
- enqueue независимые утренние события best-effort;
- по умолчанию ставит в очередь:
  - `cleanup_job_statuses` с retention `24` часа;
  - `send_reminders` в утреннем режиме;
- failure одной команды не блокирует enqueue остальных;
- в субботу и воскресенье reminder logic всё ещё может дать structured no-op, но сам `morning` не считается reminder-specific mode.

### `test`
- безопасный operator/developer mode;
- использует test-chat routing и safe defaults там, где это предусмотрено.

## Transport mapping

- HTTP runtime requests идут через:
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/runtime/runtime_shell.py`
- scheduled triggers идут через:
  - `src/entrypoints/triggers/trigger_shell.py`
- queue worker jobs исполняют explicit command jobs без ad-hoc mode routing.

## Неподдерживаемые старые режимы

Planner/store-era modes больше не входят в стандартный runtime.

Поведение:
- HTTP возвращает structured unsupported response;
- runtime/debug shell возвращает `unsupported_mode`.

## Timezone policy

- human-facing render timestamps используют `runtime.timezone` (по умолчанию `Europe/Moscow`);
- system/JSON timestamps остаются в UTC ISO.

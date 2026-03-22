# Схема статусов задач

`src/platform/runtime/worker/status_store.py` — это operational source of truth для недавних command executions.

Статусы используются для:
- `/info`;
- скрытого admin endpoint `/admin/jobs/{job_id}`;
- retry/terminal failure visibility;
- коротких операторских расследований без полного log search.

## Record shape

Обязательные поля:
- `job_id`
- `command_type`
- `status`
- `requested_at_utc`

Необязательные поля:
- `started_at_utc`
- `finished_at_utc`
- `requested_by`
- `summary`
- `warnings`
- `retryable`
- `error`

## Канонические статусы

- `accepted`
- `running`
- `success`
- `failed_retryable`
- `failed_terminal`

Исторические старые значения могут встречаться в старых объектах, но новые записи должны использовать только этот набор.

## Смысл статусов

### `accepted`
Команда принята intake layer и записана в status store.

### `running`
Worker начал выполнение.

### `success`
Команда завершилась успешно.

### `failed_retryable`
Команда завершилась с transient failure, ожидается retry.

### `failed_terminal`
Команда завершилась с terminal failure и не должна ретраиться transport layer.

## `summary` и `error`

`summary` — короткая безопасная для operator UI структурированная информация:
- render counters
- notify counters
- target sheet info
- snapshot summary fields

`error` — короткая структурированная ошибка:
- `code`
- `message`
- optional bounded technical fields

Без секретов и без больших payload dumps.

## Storage layout

- `jobs/{env}/status/{job_id}.json`
- `jobs/{env}/latest/{command_type}.json`
- `jobs/{env}/history/index.json`
- `jobs/{env}/history/by-command/{command_type}.json`

## Retention

- последние `50` jobs overall
- последние `20` jobs per command type

Этого достаточно для `/info` и коротких operator investigations.  
Это не замена долгосрочным логам.

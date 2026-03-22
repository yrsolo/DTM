# Runbook

Это минимальный operator runbook для текущего контура.

## 1. Локальный запуск

1. Создай `.env.dev` или скопируй `.env.dev.example`.
2. Подай Google credentials через поддерживаемые env inputs.
3. Проверь Object Storage credentials для snapshot и job-status путей.

## 2. Snapshot refresh

Канонический refresh flow:

1. прочитать Google Sheets;
2. нормализовать raw snapshot;
3. смержить extra metadata;
4. записать raw/prep snapshots в Object Storage.

Канонический read path после этого:
- browser/API читают prep snapshot;
- render/reminder/group-query используют тот же read-model контур.

## 3. Browser и auth

Backend часть browser auth описана отдельно:
- [browser-auth.md](browser-auth.md)
- [../reference/browser-auth.md](../reference/browser-auth.md)

Используй их, когда нужно:
- проверить trusted ingress;
- понять masked/full behavior;
- проверить `/ops/auth/*` и `/ops/api/*` разделение.

## 4. Reminder и Telegram

- reminder runtime читает задачи из prep snapshot;
- people routing идёт через people snapshot;
- webhook intake в Telegram должен быстро parse -> route -> enqueue -> return.

Отдельный operator note:
- [telegram-webhook.md](telegram-webhook.md)

## 5. `/info`

`/info` — операторская точка входа для:
- snapshot state;
- queue live state;
- job history;
- build/runtime metadata;
- attachment harness;
- bottleneck traces и telemetry.

Если нужно быстро понять, что происходит в живом контуре, начинай с `/info`.

## 5.1. Cleanup старых job statuses

`jobs/{env}/status/{job_id}.json` — это короткоживущий operational lookup, а не долгосрочный архив.

Канонический cleanup:
- nightly/утренний maintenance идёт через `morning` trigger;
- по умолчанию удаляются terminal statuses старше `24` часов;
- `latest/*` и `history/*` сохраняются как компактная operator-facing память.

Ручной enqueue:
- `POST /admin/commands/cleanup-job-statuses`

Поддерживаемый payload:
- `delete_before_utc` — точный UTC cutoff в ISO-8601;
- `older_than_hours` — retention относительно текущего времени;
- `dry_run` — только посчитать, ничего не удалять;
- `limit` — ограничить число eligible deletions за один запуск.

Ограничения:
- задавай либо `delete_before_utc`, либо `older_than_hours`;
- команда не трогает `accepted` и `running`;
- команда не удаляет `jobs/{env}/latest/*` и `jobs/{env}/history/*`.

## 6. Attachments

Канонический operator flow:

1. `request-upload`
2. direct PUT в Object Storage
3. `finalize`
4. worker attach publication
5. `view` / `download` / `delete`

Важно:
- attachment success меряется публикацией во frontend payload;
- `test` contour smoke уже подтверждён;
- `prod` smoke остаётся blocked до ручного production release workflow.

## 7. Branching и deploy

1. Разработка идёт в `dev`.
2. `test` deploy идёт через активный workflow для test.
3. `prod` release остаётся owner-controlled и запускается вручную.

## 8. Guardrails

Перед shipping structural cleanups:

- `python scripts/check_no_monsters.py`
- `python scripts/check_entrypoint_import_boundaries.py`
- `python scripts/check_active_import_boundaries.py`

## 9. История

Исторические runbook'и, migration-era notes и superseded operator docs лежат только в `archive/docs/`.

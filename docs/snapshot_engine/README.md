# Snapshot Engine

`Snapshot Engine` — канонический runtime-контур для API v2 и group-query после hard cutover.

Путь данных:
1. Sheets snapshot (`values + colors`)
2. normalize -> `RawSnapshot`
3. merge extra -> `PrepSnapshot`
4. запись `raw/prep/extra` в S3
5. query из `PrepSnapshot` для HTTP/notify

Ключевые инварианты:
- `status` = нормализованный color-derived статус
- `history` = сырой текстовый статус из таблицы
- `task_id` = ID из исходной таблицы (канонический идентификатор)

Runtime больше не использует YDB readmodel как source-of-truth для API v2.

Изоляция test/prod в одном бакете:
- `prefix_raw/prefix_prep/prefix_extra` поддерживают шаблон `{env}`.
- Для `ENV=test` ключи пишутся в `snapshots/test/...`.
- Для `ENV=prod` ключи пишутся в `snapshots/prod/...`.

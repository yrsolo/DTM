# Контракты

Этот документ фиксирует текущие runtime contracts системы.  
Исторические storage/schema детали в active canon не входят.

## 1. Normalized task contract

Минимальные канонические поля задачи:
- `task_id`
- `title`
- `brand`
- `format_`
- `customer`
- `owner_id`
- `group_id`
- `raw_timing`
- `status`
- `history`
- `min_date`
- `max_date`
- `milestones`

Важно:
- `status` — нормализованный workflow status;
- `history` — исходный human-facing status/history text;
- task identity стабильна внутри snapshot-based runtime contour.

## 2. Milestone contract

Поля milestone:
- `idx`
- `type`
- `planned`
- `actual`
- `status`
- `raw_text`

Инвариант:
- `milestones` не должны быть пустыми в runtime task view.

## 3. Snapshot contracts

### Raw snapshot

Нормализованное состояние source data до merge с extra metadata.

### Prep snapshot

Канонический read-side snapshot для:
- frontend/API reads;
- render jobs;
- reminder flows;
- group-query selection;
- attachment visibility.

### Extra snapshot

Bulk metadata поверх raw/prep snapshots:
- attachment metadata;
- orphan flags;
- прочая вспомогательная task metadata.

## 4. Attachment metadata

- `attachment_id`
- `task_id`
- `filename_original`
- `filename_display`
- `mime_type`
- `kind`
- `size_bytes`
- `status`
- `storage_bucket` (internal only)
- `storage_key` (internal only)
- `storage_etag`
- `storage_version`
- `uploaded_by_user_id`
- `uploaded_at`
- `verified_at`
- `deleted_at`
- `deleted_by_user_id`
- `error_code`
- `error_message`
- `snapshot_visible`
- `preview_capabilities`

## 5. Frontend payload contract

Каноническая структура ответа:
- `meta`
- `filters`
- `summary`
- `entities`
- `tasks`

Гарантии:
- filtering идёт по prep snapshot;
- masking меняет чувствительные значения, но не форму payload;
- `milestones` остаются полными;
- ids, dates, statuses и summary/meta structure стабильны между `full` и `masked`.

Attachment guarantees:
- `tasks[].attachments` содержит только `ready` и visible attachments;
- frontend DTO не раскрывает storage internals;
- masked mode возвращает пустые attachments arrays.

## 6. Hashing и freshness

Stable source hash:
- строится из стабильного JSON по sheet values/colors;
- используется для решения, нужен ли rebuild.

Content-level task hashing:
- должен учитывать milestone timing fields;
- не должен переопределяться косметическими маркерами.

## 7. Related reference

Режимы runtime описаны в [runtime-modes.md](runtime-modes.md).  
Исторические schema details лежат в `archive/docs/`.

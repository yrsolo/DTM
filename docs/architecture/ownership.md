# Ownership Map

## Главные owning modules

- `access_api` — хозяин первичного browser read-model
- `attachments` — lifecycle вложений и publication readiness
- `snapshot` — ingestion, state build и read-model projection
- `rendering` — sheet rendering use-cases
- `reminders` — reminder selection, payload build и delivery orchestration
- `telegram_interaction` — Telegram intake и reply-related flows

## Кто чем не владеет

- `platform` не владеет бизнес-логикой модулей
- `entrypoints` не владеют read-side или mutation semantics
- `snapshot` не владеет browser delivery
- `attachments` не владеет frontend cache/read delivery
- `telegram_interaction` не должен перетягивать архитектуру на себя

## Главные finish lines

- Основной read-side finish line: первичный browser read-model из `access_api`
- Attachment publication finish line: видимость attachment в основном task-list payload
- Operator finish line: данные и диагностика в `/info`

## Как читать ownership

Если нужно понять сценарий, начинай с owning module, а не с transport shell или bootstrap.

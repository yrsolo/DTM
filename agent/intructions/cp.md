# Legacy `.doc` Preview Via External PDF Converter

## Summary
Реализовать split-flow только для legacy `.doc` (`application/msword`):
- `download` всегда отдаёт исходный `.doc`
- `view` открывает только derived PDF preview
- preview генерируется асинхронно после успешного `attach_task_file`
- `.docx`, `.pdf`, изображения не меняют текущее поведение

Внешний converter использовать через secret-only integration:
- URL контейнера и shared token не хранить в repo
- прокинуть их из Lockbox в runtime env
- backend вызывает converter по `source_url -> target_url` контракту

Выбранный дефолт для совместимости с текущим converter API:
- для preview upload backend генерирует presigned `target_url` без обязательных signed headers
- converter не нужно расширять под `target_headers`

## Key Changes
### 1. Converter integration and config
- Добавить typed converter client в application layer, вызывающий `POST /convert/doc-to-pdf` с `X-Shared-Token`.
- Конфигурировать client только через env, поднимаемые из Lockbox в deploy/release workflows.
- Добавить runtime bootstrap wiring так, чтобы при отсутствии converter secrets:
  - система продолжала работать для всех attachment типов
  - `.doc` preview generation помечалась как unavailable/failure, без падения attach flow целиком

### 2. Attachment preview lifecycle for `.doc`
- Использовать уже существующие metadata fields:
  - `preview_state`: `none | pending | ready | failed`
  - `derived_preview_ref`
- После успешного `attach_task_file`:
  - для `.doc` сразу выставлять `preview_state=pending`
  - enqueue нового internal command `generate_attachment_preview`
- Новый job:
  - находит attachment metadata
  - убеждается, что attachment ещё `ready` и не `deleted`
  - строит `source_url` на исходный `.doc`
  - строит deterministic preview key, например `attachments/{env}/{task_id}/{attachment_id}/preview.pdf`
  - получает presigned preview `target_url`
  - вызывает converter
  - при успехе записывает `preview_state=ready`, `derived_preview_ref=<preview key>`
  - при ошибке записывает `preview_state=failed` и warning/details для диагностики
- Job должен быть idempotent:
  - если preview уже `ready` и `derived_preview_ref` валиден, повторно не конвертировать

### 3. Read-path contract
- `download`:
  - для всех типов остаётся текущим
  - для `.doc` всегда ведёт на исходный `storage_key`
- `view`:
  - для `.doc`:
    - `preview_state=ready` -> redirect на derived PDF preview
    - `preview_state=pending` -> `409` JSON error `attachment_preview_pending`
    - `preview_state=failed` или preview отсутствует -> `503` JSON error `attachment_preview_unavailable`
  - для `.docx`, `.pdf`, image поведение не меняется
- `AttachmentReadResolver` расширить preview-aware логикой, не меняя route shapes.
- `tasks[].attachments[].capabilities` для `.doc` сменить с `doc_view` на preview semantics, например:
  - `browser_view`
  - `download`
  - `pdf_preview`
- `links.view` и `links.download` оставить без изменения.

### 4. Delete, operator UI, docs
- Delete flow для `.doc` должен best-effort удалять:
  - исходный `.doc`
  - derived `preview.pdf`
- `/info` attachment harness обновить:
  - показывать `preview_state`
  - для `.doc` явно писать, что `view` открывает PDF preview, а `download` — original `.doc`
- Обновить docs:
  - `docs/integrations/attachments/backend-flow.md`
  - `docs/integrations/attachments/frontend-handoff.md`
  - при необходимости browser-auth runbook, если фиксируется новое observable `409/503` поведение на `view`

## Public Interfaces
- Новый internal command type: `generate_attachment_preview`
- Новые error codes на read-path:
  - `attachment_preview_pending`
  - `attachment_preview_unavailable`
- Capability semantics for `.doc`:
  - убрать `doc_view`
  - добавить `pdf_preview`
- Новые env secrets в bootstrap/deploy:
  - converter base URL
  - converter shared token

## Test Plan
- Policy/unit:
  - `.doc` остаётся в upload allowlist
  - `.doc` capabilities отражают preview-via-pdf semantics
- Job tests:
  - `attach_task_file` для `.doc` enqueue-ит `generate_attachment_preview`
  - preview job на success ставит `preview_state=ready` и `derived_preview_ref`
  - converter failure даёт `preview_state=failed`
  - повторный preview job idempotent
- Read-path tests:
  - `.doc` `download` выдаёт original key
  - `.doc` `view` редиректит на preview PDF when ready
  - `.doc` `view` даёт `409 attachment_preview_pending` when pending
  - `.doc` `view` даёт `503 attachment_preview_unavailable` when failed/missing
  - `.docx`, `.pdf`, image read behavior unchanged
- Delete tests:
  - `.doc` delete best-effort удаляет original и preview object
- `/info` tests:
  - harness показывает `preview_state`
  - `.doc` card корректно отражает split behavior
- Acceptance on `test`:
  - upload `.doc`
  - дождаться `attach_task_file=success`
  - дождаться `generate_attachment_preview=success`
  - `view` открывает PDF
  - `download` отдаёт original `.doc`
  - `delete` удаляет attachment и preview

## Assumptions
- Внешний converter остаётся на текущем контракте `/convert/doc-to-pdf` и не требует изменений.
- Preview upload contract можно безопасно генерировать без signed `Content-Type`, чтобы converter использовал только `target_url`.
- Если converter временно недоступен, attach `.doc` всё равно считается успешным, а проблема локализуется только в preview lifecycle.
- Preview нужен только для `.doc`; `.docx` intentionally не конвертируется.

# `attachments`

## Роль

`attachments` владеет жизненным циклом вложений:
- request-upload;
- finalize;
- attach/delete mutations;
- preview lifecycle;
- publication readiness;
- read access policy для view/download.

## Канонический сценарий

1. Backend выдаёт upload contract.
2. Браузер загружает бинарник напрямую в Object Storage.
3. `finalize` подтверждает объект и ставит mutation в очередь.
4. Worker публикует metadata в snapshot-based read-model.
5. Вложение становится видимым в основном browser payload.

## Что модуль не должен делать

- управлять frontend cache как самостоятельный owner;
- отдавать основной browser payload;
- прятать success-criteria в transport shell.

## Finish line

Вложение считается опубликованным не в момент upload или finalize, а когда оно появилось в основном task-list payload.

## Где смотреть дальше

- [../architecture/runtime-flow.md](../architecture/runtime-flow.md)
- [../operations/runbook.md](../operations/runbook.md)

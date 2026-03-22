# `snapshot`

## Роль

`snapshot` владеет read-model контуром:
- ingestion из источников;
- normalization;
- state build/update;
- prepared snapshot storage;
- projection attachment state в основной read-side.

## Главные входы

- `update_snapshot`;
- query/read APIs для других модулей;
- attachment mutation support там, где metadata должна стать частью read-model.
- role-true internal builders вместо одного общего runtime hub:
  - stores,
  - query runtime,
  - attachment mutation runtime,
  - update runtime.

## Что модуль не должен делать

- становиться browser delivery layer;
- становиться transport-owned engine;
- собираться вокруг одного широкого internal runtime bag;
- тянуть ownership других модулей к себе.

## Finish line

Если изменение стало видимым в подготовленном read-model, это finish line `snapshot`.

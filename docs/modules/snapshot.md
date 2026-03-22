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

## Что модуль не должен делать

- становиться browser delivery layer;
- становиться transport-owned engine;
- тянуть ownership других модулей к себе.

## Finish line

Если изменение стало видимым в подготовленном read-model, это finish line `snapshot`.

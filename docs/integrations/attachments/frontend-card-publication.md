# Frontend Card Publication Scenario

Этот документ описывает продуктовый и архитектурный смысл attachment flow в DTM.

Главный сценарий:
- админ загружает ТЗ в attachment задачи;
- система принимает `request-upload` и `finalize` как начало mutation flow;
- async обработка конвертирует и публикует attachment;
- админ следит за job status и ждёт появления attachment в карточке;
- frontend делает refetch или polling и получает уже кэшированный payload карточки с attachment;
- обычный пользователь открывает карточку и быстро видит attachment без тяжёлой сборки на каждый запрос.

## Главный критерий успеха

Успех attachment flow означает не просто:
- файл принят в storage;
- `finalize` вернул `202`;
- async job дошёл до terminal state.

Успех означает:
- attachment появился в browser-facing cached task card payload;
- attachment виден в карточке по обычному read path;
- frontend не ждёт тяжёлую rebuild-операцию на открытии карточки.

Если файл существует, но не попал в карточку, сценарий ещё не завершён.

## Сквозной поток

1. Админ запрашивает upload contract через attachment auth/API route.
2. Браузер напрямую загружает бинарник в Object Storage.
3. Админ вызывает `finalize`.
4. Backend ставит mutation/publication работу в очередь.
5. Worker проверяет объект, сохраняет metadata, при необходимости запускает preview/conversion.
6. Attachment становится пригодным к публикации в read-side.
7. Runtime инициирует invalidation/refresh нужного read-side контура.
8. `snapshot` включает attachment в задачу как часть read-model projection.
9. `access_api` отдаёт карточку через обычный browser-safe cached payload.
10. Админ после terminal job success и refetch видит attachment в карточке.
11. Обычный пользователь открывает карточку и быстро получает уже подготовленный ответ.

## Кто за что отвечает

### `attachments`

Отвечает за mutation lifecycle:
- `request-upload`, `finalize`, `delete`;
- metadata;
- preview/conversion lifecycle;
- publication readiness;
- attachment read policy и capability metadata.

Не отвечает за:
- прямое управление frontend cache;
- browser card payload как конечный read-side артефакт.

### `platform/runtime`

Отвечает за orchestration после mutation:
- invalidation intent;
- refresh scheduling;
- eventual freshness после attach/delete/preview completion;
- operator-observable job progression.

Runtime не должен быть местом attachment business rules, но именно он координирует переход `mutation -> updated read-side`.

### `snapshot`

Отвечает за read-model projection:
- attachment становится частью карточки задачи именно здесь;
- read-side включает только уже пригодные к публикации attachment-данные;
- browser card не должна собираться напрямую из mutation state.

### `access_api`

Отвечает за browser-facing delivery:
- cached task card payload;
- browser-safe shaping;
- выдачу attachment внутри карточки;
- предсказуемый быстрый read path для frontend.

## Сигналы готовности для frontend и оператора

Что не означает готовность:
- успешный direct upload;
- успешный `finalize`;
- сам по себе факт существования файла в storage.

Что означает readiness:
- terminal attachment job success;
- attachment опубликован в read-side карточки;
- после refetch attachment появился в обычном task card payload.

Практическое следствие:
- frontend может использовать polling/refetch после terminal job success;
- backend должен обеспечить eventual publication into cached card payload;
- attachment flow нельзя считать завершённым раньше появления attachment в карточке.

## Нефункциональные ожидания

- API карточки остаётся быстрым.
- Карточка читается из кэша или подготовленного snapshot/read-side слоя.
- Attachment mutation не должна превращать обычный card read в тяжёлый синхронный pipeline.
- Пользователь не должен знать о внутренних storage/conversion деталях.

## Архитектурный вывод

Этот сценарий задаёт governing pipeline для attachment-related waves:

`attachments mutation -> platform/runtime invalidation/orchestration -> snapshot projection -> access_api cached delivery`

Именно этот путь, а не upload-only flow, должен считаться каноническим acceptance path для recovery-работ вокруг attachments, cache freshness, snapshot и access API.

# Runtime Flow

## Главный read-path

1. Источники данных читаются и нормализуются в `snapshot`.
2. `snapshot` строит подготовленный read-model.
3. `access_api` собирает browser-safe payload.
4. HTTP entrypoint отдаёт его без глубокой бизнес-логики в transport layer.

Именно этот путь считается основным пользовательским чтением системы.

## Главный mutation-path

1. HTTP, webhook или trigger intake принимает запрос.
2. Entry layer валидирует и маршрутизирует его в owning module или runtime shell.
3. Mutation чаще всего превращается в command queue job.
4. Worker исполняет job в owning module.
5. Результат mutation становится видимым через обновлённый read-model.

## Attachment publication

Для вложений важно различать:

- upload acceptance;
- finalize acceptance;
- publication readiness;
- фактическую видимость во frontend payload.

Канонический успешный исход — вложение появилось в основном browser payload после worker execution и read-model refresh.

## Runtime after-effects

`platform` владеет только runtime concerns:

- config/bootstrap;
- queue/worker execution shells;
- infra integrations;
- publication aftermath там, где это уже не ownership модуля, а runtime-coordination.

# Обзор архитектуры

DTM — это модульный монолит с одним главным browser read-model и явными async-мутаторами.

## Базовая картина

- `entrypoints/` принимают HTTP, trigger и worker-события.
- `platform/` собирает runtime, интеграции, infra и shell-seams.
- `contexts/` владеют прикладными сценариями.
- `core/` хранит общий доменный слой и чистые правила.

## Главная идея

Система оптимизирована под стабильное чтение.

- данные из источников нормализуются и собираются в `snapshot`;
- браузер читает первичный browser read-model из `access_api`;
- тяжёлые и мутирующие действия идут через очередь;
- публикация результата считается завершённой только тогда, когда он виден в основном browser payload.

## Что важно не путать

- `platform` не владеет бизнес-сценариями модулей;
- `entrypoints` не должны становиться местом orchestration;
- `snapshot` важен как read-model контур, но не как скрытый центр мира;
- `/info` — операторская поверхность, а не отдельный продуктовый контур.

## Текущая активная карта

- `src/config` — typed config loading
- `src/core` — shared domain rules
- `src/contexts` — owning modules
- `src/entrypoints` — thin intake/execution shells
- `src/platform` — runtime assembly, integrations, infra

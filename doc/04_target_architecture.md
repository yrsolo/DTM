# Целевая архитектура (новая основа)

## Позиция
Проект переводим на новую архитектурную основу. Легаси не является ограничением: допускается несовместимое внутреннее изменение модулей при сохранении требуемого бизнес-результата.

## Архитектурный стиль
- `Clean Architecture` + `Hexagonal (Ports and Adapters)`.
- Домен и use-case слой не знают о Google Sheets/Telegram/OpenAI.
- Все внешние системы подключаются через адаптеры.

## Слои системы

## 1) `domain`
Ответственность:
- бизнес-сущности и инварианты;
- правила парсинга таймингов;
- правила видимости стадий;
- расчет дедлайнов/следующего рабочего дня.

Не содержит:
- HTTP-клиентов;
- Google/Telegram/OpenAI SDK;
- чтения `.env`.

## 2) `application`
Ответственность:
- orchestrate бизнес-сценарии (use cases):
  - синхронизация задач;
  - построение витрин;
  - формирование и отправка напоминаний;
  - получение snapshot для UI.
- транзакционные границы и порядок шагов.

## 3) `ports`
Ответственность:
- контракты (интерфейсы) доступа к данным и внешним сервисам:
  - `TaskSourcePort`;
  - `PeopleSourcePort`;
  - `BoardWriterPort`;
  - `NotifierPort`;
  - `LLMPort`;
  - `ClockPort`.

## 4) `adapters`
Ответственность:
- конкретные реализации портов:
  - Google Sheets source/writer;
  - Telegram sender;
  - OpenAI enhancer;
  - Yandex trigger adapter;
  - локальные mock/fake адаптеры.

## 5) `interfaces`
Ответственность:
- CLI entrypoint;
- cloud function handler;
- future REST API/WebSocket для UI.

---

## Целевой формат хранения данных

## Источник истины (этап 1)
- Основной источник: Google Sheets (до полной миграции UI).
- Чтение и запись разведены:
  - `SOURCE_*` - таблица-источник;
  - `TARGET_*` - таблица-приемник/витрина.

## Канонический внутренний формат (в коде)
- Все входные данные приводятся к каноническим схемам:
  - `TaskRecord`
  - `TaskStageRecord`
  - `PersonRecord`
  - `ReminderDraft`
- Формат: Pydantic-модели (или dataclass + strict validation).
- Даты в UTC/ISO внутри системы, timezone для сообщений/витрин применяется на адаптере.

## Целевое хранение (этап 2)
- `PostgreSQL` как основное хранилище:
  - `tasks`
  - `task_stages`
  - `people`
  - `notifications`
  - `sync_runs`
  - `board_snapshots`
- Google Sheets остается внешней интеграцией импорта/экспорта, но не доменным источником.

## Формат обмена для UI/API
- JSON read-model:
  - `board.timeline`
  - `board.by_designer`
  - `task.details`
  - `alerts`
- Версионирование схемы (`schema_version`) обязательно.

---

## Целевая структура папок

```text
TABLE_PARSE/
  src/
    domain/
      entities/
      value_objects/
      services/
      rules/
    application/
      use_cases/
      dto/
      orchestrators/
    ports/
      inbound/
      outbound/
    adapters/
      inbound/
        cli/
        cloud/
        api/
      outbound/
        google_sheets/
        telegram/
        openai/
        postgres/
        observability/
    infrastructure/
      config/
      logging/
      security/
      time/
    tests/
      unit/
      integration/
      contract/
      golden/
    scripts/
      dev/
      migration/
  doc/
  .env.example
  pyproject.toml
  README.md
```

---

## Целевые модули и ответственности

## `SyncTasksUseCase`
- читает задачи из `TaskSourcePort`;
- валидирует/нормализует в `TaskRecord`;
- сохраняет в хранилище;
- формирует отчет синка.

## `BuildDesignerBoardUseCase`
- строит read-model "задачи по дизайнерам";
- отдает в `BoardWriterPort` (Sheets/UI/API).

## `BuildTimelineBoardUseCase`
- строит read-model "задачи по датам/этапам";
- пишет в целевую витрину.

## `PrepareRemindersUseCase`
- берет задачи на сегодня/следующий рабочий день;
- строит строгий черновик без LLM;
- опционально улучшает через `LLMPort`;
- отдает готовые сообщения.

## `SendRemindersUseCase`
- отправляет через `NotifierPort`;
- обеспечивает идемпотентность отправки;
- пишет событие в `notifications`.

## `RunPipelineUseCase`
- единая точка сценариев `timer/morning/test`;
- конфигурирует dry-run;
- публикует метрики прогона.

---

## Правила модульной ответственности
- Один модуль = одна причина изменения.
- Никакой бизнес-логики в адаптерах.
- Никаких вызовов API из domain/application без порта.
- Любой внешний формат приводится к DTO на входе.
- Любой выход наружу строится отдельным mapper/renderer.

---

## Нефункциональные требования новой основы
- Наблюдаемость: структурные логи + метрики + trace id.
- Надежность: retry/backoff/circuit-breaker в внешних адаптерах.
- Безопасность: секреты только из env/secret manager, masking PII в логах.
- Масштабируемость: раздельный запуск синка и рассылки.
- Расширяемость: подключение нового UI без переписывания domain/application.

---

## Что это меняет относительно текущего состояния
- Убираем "все в одном planner".
- Переносим правила из `constants.py` в типизированные конфиги и domain rules.
- Четко разводим:
  - откуда читаем данные;
  - куда рендерим результат;
  - как и когда отправляем уведомления.
- Готовим систему к переходу от Google Sheets-визуализации к отдельному интерфейсу.

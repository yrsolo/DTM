````md
# DTM — полное ТЗ на архитектурную переделку проекта

## Статус документа

Этот документ задаёт **целевую архитектуру**, **правила устройства репозитория**, **кампании по переделке**, **конкретные технические задачи**, **целевые скелеты папок и модулей**, а также **жёсткие запреты**, которые не позволят проекту снова скатиться в смешанную, трудно читаемую структуру.

Цель переделки:

- сделать кодовую базу **очень понятной визуально**;
- сделать проект **модульным монолитом** с возможностью в будущем выносить куски в отдельные сервисы;
- сохранить текущую технологическую выгоду единого deployment/runtime;
- сделать так, чтобы вход в систему, маршрутизация и выполнение сценариев были **прозрачны с первого взгляда**;
- ослабить связанность;
- не потерять текущие очереди, fan-out, триггеры, attachment workflow, reminder flow, snapshot/render flow;
- превратить проект в репозиторий, который можно показывать как пример **чистой организации**.

---

# 1. Главная архитектурная идея

## 1.1. Целевой стиль архитектуры

Проект должен быть оформлен как **modular monolith**:

- один runtime / один deployment unit;
- одна Cloud Function или эквивалентный единый процесс исполнения;
- несколько **автономных контекстов** внутри;
- жёсткие границы между контекстами;
- взаимодействие между контекстами только через:
  - публичные фасады;
  - контракты;
  - внутренние команды;
  - orchestration layer.

Проект **не должен** выглядеть как один большой app, где всё друг друга импортирует.

Проект **не должен** выглядеть как набор технических слоёв без доменных границ.

Проект **не должен** выглядеть как зачаток микросервисов с избыточной абстракцией.

Проект **должен** выглядеть как:
- единая система;
- с очень простой верхней точкой входа;
- с явными режимами исполнения;
- с небольшим количеством крупных контекстов;
- с понятной ownership-картой.

---

## 1.2. Что считаем первым уровнем архитектуры

Первый уровень системы — это **не** `jobs`, **не** `worker`, **не** `http`, **не** `telegram`, **не** `ydb`.

Первый уровень системы — это:

- `platform.runtime`
- `snapshot`
- `rendering`
- `reminders`
- `telegram_interaction`
- `attachments`
- `access_api`

Именно это должно быть видно в репозитории как главная карта системы.

---

## 1.3. Базовый принцип

Сначала система должна ответить на вопрос:

> **какой режим исполнения пришёл?**

И только потом:
- импортировать нужный контекст;
- строить его зависимости;
- выполнять работу.

Нельзя на старте поднимать “всю вселенную”.

---

# 2. Главные архитектурные проблемы текущего состояния

## 2.1. Проект выглядит как несколько разных систем сразу

Сейчас в кодовой базе одновременно видны:

- runtime/triggers;
- queue-based execution;
- доменные сценарии;
- legacy-следы;
- слой jobs как псевдо-архитектурный центр.

В результате разработчик не сразу понимает:
- что в проекте является главным;
- какие куски — самостоятельные модули;
- где реальные архитектурные границы.

---

## 2.2. Доменные границы не доминируют над транспортными

Сейчас сильнее видны:
- HTTP;
- worker;
- triggers;
- jobs.

А должны сильнее видны:
- snapshot;
- rendering;
- reminders;
- attachments;
- access_api;
- telegram_interaction.

---

## 2.3. “Jobs” и “worker” сейчас выглядят как центр мира

Это удобно для исполнения, но плохо для читаемости.

`jobs` — это **не модульная карта**.
`worker` — это **не доменная ось**.

Они должны остаться частью runtime/platform, но перестать быть визуальным центром репозитория.

---

## 2.4. Слишком высок риск снова свалить всё в общий bootstrap

Если не зафиксировать жёсткие ограничения, то после переделки есть высокий риск, что:
- entrypoint снова обрастёт логикой;
- bootstrap снова станет супермодулем;
- модули начнут импортировать внутренности друг друга;
- появится новый “shared” со всем подряд;
- runtime начнёт знать слишком много о бизнес-логике.

---

# 3. Целевая архитектурная карта

## 3.1. Слои первого уровня

### 3.1.1. `platform.runtime`
Назначение:
- классификация входящих событий;
- routing по mode;
- transport shells;
- orchestration triggers;
- queue intake / queue dispatch;
- общая observability;
- общие low-level runtime primitives.

Это **не бизнес-модуль**.

---

### 3.1.2. `snapshot`
Назначение:
- ingestion данных;
- чтение источников;
- нормализация;
- сбор и обновление snapshot/state;
- подготовка read-side данных;
- query engine для подготовленного состояния.

Это модуль, который владеет **данными состояния и их обновлением**.

---

### 3.1.3. `rendering`
Назначение:
- генерация представлений;
- timeline sheet;
- designers sheet;
- render/writeback сценарии.

Это модуль, который владеет **представлениями**, но не исходным snapshot ingestion.

---

### 3.1.4. `reminders`
Назначение:
- отбор задач для напоминаний;
- формирование reminder payload;
- стилизация текста;
- delivery orchestration;
- retry/send accounting.

Это модуль, который владеет **логикой напоминаний**, а не триггерами “morning”.

---

### 3.1.5. `telegram_interaction`
Назначение:
- Telegram webhook intake;
- parsing telegram update;
- mapping update → internal command;
- group/user interaction flows;
- reply orchestration для Telegram-сценариев.

Это модуль взаимодействия, а не просто “адаптер Telegram API”.

---

### 3.1.6. `attachments`
Назначение:
- upload contract;
- finalize;
- attach metadata;
- preview lifecycle;
- delete lifecycle;
- stale cleanup;
- attachment access/read policy.

Это самостоятельный модуль с собственным workflow.

---

### 3.1.7. `access_api`
Назначение:
- frontend-facing HTTP surface;
- masked/open режимы;
- auth/access policy;
- safe payload assembly;
- browser-facing DTO.

Это модуль внешнего API-контракта.

---

## 3.2. Что не является модулем первого уровня

Следующие сущности **не должны** оформляться как отдельные доменные модули:

- `jobs`
- `worker`
- `triggers`
- `http`
- `ydb`
- `telegram`
- `openai`
- `s3`
- `storage`

Это либо transport/runtime, либо infrastructure adapters.

---

# 4. Целевая структура репозитория

## 4.1. Корневая структура

```text
DTM/
  README.md
  pyproject.toml
  docs/
    overview/
    architecture/
    modules/
    operations/
    reference/
  src/
    entrypoint/
    platform/
    shared/
    contexts/
      snapshot/
      rendering/
      reminders/
      telegram_interaction/
      attachments/
      access_api/
  tests/
    unit/
    integration/
    architecture/
  scripts/
  tools/
  work/
  agent/
  archive/
````

---

## 4.2. Назначение корневых директорий

### `docs/`

Только актуальная документация проекта.

### `src/`

Только активный runtime-код.

### `tests/`

Все тесты.

### `scripts/`

Служебные проверки и developer scripts.

### `tools/`

Вспомогательные инженерные инструменты, не runtime.

### `work/`

Планы, кампании, execution tracking.

### `agent/`

Инструкции и материалы для агентной работы.

### `archive/`

Всё устаревшее, legacy, historical, migration-only.

---

## 4.3. Жёсткий запрет

В корне не должно остаться нескольких “живых” code roots вроде:

* `core/`
* `utils/`
* `old/`
* параллельного `src/core/`
* активных legacy-контуров вне `archive/`

Активный код должен жить **только в `src/`**.

---

# 5. Целевая структура `src/`

## 5.1. Общая форма

```text
src/
  entrypoint/
    handler.py
    parse_request.py
    modes.py
    responses.py

  platform/
    runtime/
      classify.py
      orchestration.py
      queue_dispatch.py
      queue_envelope.py
      telemetry.py
    config/
      loader.py
      models.py
      secrets.py
    infra/
      queue/
      storage/
      db/
      llm/
      telegram/
      sheets/
    shell/
      http.py
      trigger.py
      worker.py

  shared/
    types/
    errors/
    result/
    ids/
    time/
    logging/
    json/
    text/
    testing/

  contexts/
    snapshot/
    rendering/
    reminders/
    telegram_interaction/
    attachments/
    access_api/
```

---

# 6. Целевая форма контекста

Каждый контекст должен иметь одинаковый, узнаваемый каркас.

## 6.1. Общий шаблон

```text
contexts/<module>/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
  policies/
  tests_support/
```

---

## 6.2. Назначение частей

### `public.py`

Единственная публичная точка входа контекста для остального мира.

### `module.py`

Сборка зависимостей этого контекста.
Локальный composition root.

### `contracts/`

DTO, commands, queries, response models, межмодульные контракты.

### `application/`

Use cases / orchestrators / handlers внутри контекста.

### `domain/`

Сущности, правила, модели, policy-логика, не завязанная на инфраструктуру.

### `adapters/`

Инфраструктурные детали этого контекста.

### `policies/`

Локальные бизнес-политики, если они крупные и не помещаются в `domain`.

### `tests_support/`

Factory helpers и test doubles, специфичные для модуля.

---

## 6.3. Строгие правила

Каждый контекст:

* может иметь сколько угодно внутренней структуры;
* но наружу торчит только через `public.py`.

Нельзя импортировать внутренности чужого контекста через:

* `contexts.other_module.application.*`
* `contexts.other_module.adapters.*`
* `contexts.other_module.domain.*`

Разрешён только импорт через:

* `contexts.other_module.public`
* `contexts.other_module.contracts`

---

# 7. Тонкая точка входа

## 7.1. Цель

Вход в систему должен быть настолько простым, чтобы любой человек, открыв один файл, мгновенно понял:

* какие вообще есть режимы;
* куда они ведут;
* какие контуры живут в системе.

---

## 7.2. Целевой `handler.py`

```python
from src.entrypoint.parse_request import parse_request
from src.entrypoint.modes import Mode

def handler(event, context):
    parsed = parse_request(event)

    match parsed.mode:
        case Mode.HTTP_ACCESS_API:
            from src.contexts.access_api.public import handle_http_request
            return handle_http_request(event, context)

        case Mode.TELEGRAM_WEBHOOK:
            from src.contexts.telegram_interaction.public import handle_telegram_webhook
            return handle_telegram_webhook(event, context)

        case Mode.QUEUE_WORKER:
            from src.platform.runtime.queue_dispatch import handle_queue_message
            return handle_queue_message(event, context)

        case Mode.TRIGGER_TIMER:
            from src.platform.runtime.orchestration import handle_timer_trigger
            return handle_timer_trigger(event, context)

        case Mode.TRIGGER_MORNING:
            from src.platform.runtime.orchestration import handle_morning_trigger
            return handle_morning_trigger(event, context)

        case Mode.HEALTHCHECK:
            from src.entrypoint.responses import ok_healthcheck
            return ok_healthcheck()

        case _:
            from src.entrypoint.responses import unknown_route_response
            return unknown_route_response(parsed)
```

---

## 7.3. Правила для entrypoint

`src/entrypoint/handler.py`:

* не содержит бизнес-логики;
* не содержит тяжёлых импортов наверху;
* не строит общий app container;
* не знает деталей модулей;
* не знает YDB/OpenAI/Telegram clients;
* не занимается parsing payload business-level смысла;
* только:

  * parse;
  * match/case;
  * lazy import;
  * delegation.

---

## 7.4. Целевой `parse_request.py`

`parse_request.py` отвечает только на вопрос:

> какой mode пришёл?

Он не должен:

* собирать зависимости;
* разбирать бизнес-команды;
* делать heavy validation;
* читать базу;
* дергать очередь;
* знать доменную семантику модулей.

---

## 7.5. Целевой `modes.py`

```python
from dataclasses import dataclass
from enum import Enum

class Mode(str, Enum):
    HTTP_ACCESS_API = "http_access_api"
    TELEGRAM_WEBHOOK = "telegram_webhook"
    QUEUE_WORKER = "queue_worker"
    TRIGGER_TIMER = "trigger_timer"
    TRIGGER_MORNING = "trigger_morning"
    HEALTHCHECK = "healthcheck"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class ParsedRequest:
    mode: Mode
    path: str | None = None
    method: str | None = None
    source: str | None = None
```

---

# 8. Platform runtime — отдельный слой, не бизнес-модуль

## 8.1. Что туда входит

`platform.runtime` должен содержать только runtime concerns:

* event classification;
* queue envelope parsing;
* orchestration of scheduled triggers;
* worker dispatch по internal command type;
* generic telemetry;
* common execution wrappers;
* retries/backoff only если они транспортные, а не бизнес-специфичные.

---

## 8.2. Чего там быть не должно

Нельзя складывать туда:

* доменную логику reminder selection;
* attachment lifecycle rules;
* rendering rules;
* access masking semantics;
* snapshot domain transforms.

---

# 9. Ownership-карта сценариев

## 9.1. Routes → owning module

### HTTP routes

* frontend/public API routes → `access_api`
* telegram webhook route → `telegram_interaction`
* attachment upload/finalize/admin/read routes → `attachments`
* healthcheck → `entrypoint/platform`

### Queue worker

* worker transport → `platform.runtime`
* command execution → owning module

### Trigger routes

* `timer` trigger → `platform.runtime` orchestration
* `morning` trigger → `platform.runtime` orchestration

---

## 9.2. Commands → owning module

Примерный целевой mapping:

* `update_snapshot` → `snapshot`
* `render_timeline_sheet` → `rendering`
* `render_designers_sheet` → `rendering`
* `send_reminders` → `reminders`
* `telegram_group_query_reply` → `telegram_interaction`
* `attach_task_file` → `attachments`
* `delete_task_attachment` → `attachments`
* `cleanup_task_attachments` → `attachments`
* `generate_attachment_preview` → `attachments`

Этот mapping должен быть явным и документированным.

---

## 9.3. Trigger orchestration plans

### `timer`

Должен приводить к enqueue следующих domain-owned commands:

* `update_snapshot`
* `render_timeline_sheet`
* `render_designers_sheet`

### `morning`

Должен приводить к enqueue:

* `send_reminders`

Важно: `timer` и `morning` — не модули, а orchestration modes.

---

# 10. Целевые контексты и их скелеты

---

## 10.1. `snapshot`

### Назначение

Владение обновлением, нормализацией и подготовкой состояния.

### Скелет

```text
contexts/snapshot/
  public.py
  module.py
  contracts/
    commands.py
    dto.py
    results.py
  application/
    update_snapshot.py
    query_snapshot.py
  domain/
    snapshot_models.py
    normalization.py
    invariants.py
  adapters/
    sheets_reader.py
    snapshot_repo.py
    people_repo.py
```

### Публичный фасад

```python
class SnapshotModule:
    def handle_command(self, command): ...
    def query(self, query): ...

def get_snapshot_module() -> SnapshotModule: ...
def handle_snapshot_command(command): ...
```

### Владеет

* sheet ingestion;
* normalization;
* snapshot persistence;
* prepared read model queries.

### Не владеет

* rendering output;
* reminder formatting;
* frontend masking;
* attachment preview.

---

## 10.2. `rendering`

### Назначение

Генерация представлений и запись render-результатов.

### Скелет

```text
contexts/rendering/
  public.py
  module.py
  contracts/
    commands.py
    results.py
  application/
    render_timeline.py
    render_designers.py
  domain/
    render_models.py
    layout_rules.py
  adapters/
    sheet_writer.py
    render_repo.py
```

### Владеет

* timeline render;
* designers render;
* sheet writeback/render output.

### Зависит от

* snapshot contracts/public API.

### Не должен

* напрямую знать ingestion details snapshot module.

---

## 10.3. `reminders`

### Назначение

Отбор задач, подготовка текста, стилизация, отправка.

### Скелет

```text
contexts/reminders/
  public.py
  module.py
  contracts/
    commands.py
    dto.py
    results.py
  application/
    send_reminders.py
    build_reminder_payloads.py
  domain/
    selection_rules.py
    message_models.py
    reminder_policies.py
  adapters/
    delivery_gateway.py
    llm_styler.py
    reminder_repo.py
```

### Владеет

* business-логикой напоминаний;
* selection rules;
* send flow;
* module-local retry if business-significant.

### Не владеет

* trigger `morning`;
* generic queue plumbing;
* raw telegram update intake.

---

## 10.4. `telegram_interaction`

### Назначение

Telegram как канал взаимодействия с пользователем.

### Скелет

```text
contexts/telegram_interaction/
  public.py
  module.py
  contracts/
    commands.py
    dto.py
  application/
    handle_webhook.py
    route_update.py
    enqueue_group_reply.py
  domain/
    telegram_update_models.py
    routing_rules.py
  adapters/
    telegram_update_parser.py
    telegram_sender.py
```

### Владеет

* webhook intake;
* parsing update;
* routing telegram scenarios;
* mapping update to internal commands.

### Не владеет

* общим reminder business flow;
* generic delivery abstraction для других модулей;
* access_api.

---

## 10.5. `attachments`

### Назначение

Самостоятельный attachment subsystem.

### Скелет

```text
contexts/attachments/
  public.py
  module.py
  contracts/
    commands.py
    queries.py
    dto.py
    results.py
  application/
    request_upload.py
    finalize_upload.py
    attach_metadata.py
    delete_attachment.py
    cleanup_stale.py
    generate_preview.py
    get_attachment.py
  domain/
    attachment_models.py
    attachment_state_machine.py
    preview_policy.py
    cleanup_policy.py
  adapters/
    object_storage.py
    attachment_repo.py
    preview_converter.py
    signed_urls.py
```

### Владеет

* upload lifecycle;
* preview lifecycle;
* read/download policy;
* stale cleanup;
* metadata attach/delete.

### Особое требование

Это один из самых близких к отдельному микросервису контуров.
Его надо проектировать особенно аккуратно:

* отдельные contracts;
* минимум внешних зависимостей;
* минимум cross-module knowledge.

---

## 10.6. `access_api`

### Назначение

Внешний HTTP API для фронта и клиентов.

### Скелет

```text
contexts/access_api/
  public.py
  module.py
  contracts/
    requests.py
    responses.py
    dto.py
  application/
    handle_http_request.py
    get_dashboard_data.py
    get_task_data.py
  domain/
    masking_rules.py
    access_policy.py
    response_shapes.py
  adapters/
    auth_provider.py
    access_repo.py
    response_serializer.py
```

### Владеет

* frontend-facing contract;
* masked/open mode;
* auth/access interpretation;
* response shape assembly.

### Не владеет

* snapshot ingestion;
* rendering jobs;
* reminder scheduling;
* attachment lifecycle internals.

---

# 11. Конкретная форма public API каждого модуля

Каждый контекст должен давать наружу **предельно ясный public facade**.

Пример целевого стиля:

```python
# contexts/rendering/public.py

from .module import get_rendering_module

def handle_command(command):
    module = get_rendering_module()
    return module.handle_command(command)
```

```python
# contexts/access_api/public.py

from .module import get_access_api_module

def handle_http_request(event, context):
    module = get_access_api_module()
    return module.handle_http_request(event, context)
```

```python
# contexts/telegram_interaction/public.py

from .module import get_telegram_module

def handle_telegram_webhook(event, context):
    module = get_telegram_module()
    return module.handle_webhook(event, context)
```

---

# 12. Целевая форма module builder

## 12.1. Принцип

У каждого контекста свой локальный composition root.

Нельзя строить один глобальный container со всеми модулями сразу.

---

## 12.2. Пример

```python
# contexts/reminders/module.py

_module = None

class RemindersModule:
    def __init__(self, send_use_case):
        self._send_use_case = send_use_case

    def handle_command(self, command):
        return self._send_use_case.execute(command)

def build_reminders_module():
    from src.platform.config.loader import load_config
    from .adapters.delivery_gateway import DeliveryGateway
    from .adapters.llm_styler import LlmStyler
    from .application.send_reminders import SendRemindersUseCase

    cfg = load_config().reminders

    delivery = DeliveryGateway(cfg)
    styler = LlmStyler(cfg)
    use_case = SendRemindersUseCase(delivery=delivery, styler=styler)

    return RemindersModule(send_use_case=use_case)

def get_reminders_module():
    global _module
    if _module is None:
        _module = build_reminders_module()
    return _module
```

---

## 12.3. Правила

* module builder знает только свой модуль;
* builder может импортировать infra;
* builder может кэшировать singleton внутри warm runtime;
* builder не должен тянуть соседние контексты напрямую, кроме их `public`/`contracts` API;
* builder не должен вырастать в новый глобальный bootstrap мира.

---

# 13. Очереди и worker flow — как сохранить и не испортить

## 13.1. Общая идея

Queue/worker механизм остаётся единым runtime-контуром, но ownership команд должен принадлежать модулям.

### Правильная форма

* queue message parsed in `platform.runtime`;
* command type resolved there;
* execution delegated в owning module.

### Неправильная форма

* worker runtime знает всю бизнес-логику всех команд.

---

## 13.2. Целевой `queue_dispatch.py`

```python
def handle_queue_message(event, context):
    envelope = parse_queue_envelope(event)
    command = decode_internal_command(envelope)

    match command.type:
        case "update_snapshot":
            from src.contexts.snapshot.public import handle_command
            return handle_command(command)

        case "render_timeline_sheet" | "render_designers_sheet":
            from src.contexts.rendering.public import handle_command
            return handle_command(command)

        case "send_reminders":
            from src.contexts.reminders.public import handle_command
            return handle_command(command)

        case "telegram_group_query_reply":
            from src.contexts.telegram_interaction.public import handle_command
            return handle_command(command)

        case "attach_task_file" | "delete_task_attachment" | "cleanup_task_attachments" | "generate_attachment_preview":
            from src.contexts.attachments.public import handle_command
            return handle_command(command)

        case _:
            raise UnknownCommandTypeError(command.type)
```

---

## 13.3. Правила для queue dispatch

* явный `match/case`, не скрытый магический dispatcher;
* список команд должен быть виден в одном месте;
* по коду должно быть понятно, какой модуль владеет какой командой;
* routing таблица должна совпадать с архитектурной документацией.

---

# 14. Оркестрация триггеров

## 14.1. Отдельный слой ответственности

Триггеры не должны уходить внутрь модулей как часть бизнес-семантики.

Нужен отдельный orchestration слой внутри `platform.runtime`.

---

## 14.2. Целевой `orchestration.py`

```python
def handle_timer_trigger(event, context):
    enqueue("update_snapshot", payload={...})
    enqueue("render_timeline_sheet", payload={...})
    enqueue("render_designers_sheet", payload={...})
    return accepted_response(...)

def handle_morning_trigger(event, context):
    enqueue("send_reminders", payload={...})
    return accepted_response(...)
```

---

## 14.3. Правила

* orchestration знает последовательность/набор внутренних команд;
* orchestration не владеет доменной логикой;
* orchestration не исполняет тяжёлую работу inline;
* orchestration не должен импортировать тяжёлые доменные зависимости без нужды.

---

# 15. Конфигурация

## 15.1. Целевая модель

Конфигурация должна собираться централизованно и возвращаться как typed object.

Нельзя читать `os.getenv()` по всему проекту.

---

## 15.2. Единственная точка загрузки

Должна существовать одна canonical точка:

* `src/platform/config/loader.py`

Она:

* читает YAML;
* читает env;
* объединяет;
* валидирует;
* возвращает typed settings object.

---

## 15.3. Целевые секции config

```python
class AppConfig:
    runtime: RuntimeConfig
    snapshot: SnapshotConfig
    rendering: RenderingConfig
    reminders: RemindersConfig
    telegram_interaction: TelegramInteractionConfig
    attachments: AttachmentsConfig
    access_api: AccessApiConfig
    infra: InfraConfig
    secrets: SecretConfig
```

---

## 15.4. Правила

* модуль получает только свой config slice;
* entrypoint не лезет в env;
* worker runtime не лезет в доменные настройки напрямую;
* доменная логика не зависит от способа хранения конфигурации.

---

# 16. Shared — минимальный и строгий

## 16.1. Что может лежать в `shared/`

Только действительно общие primitives:

* Result/Either-like abstractions;
* common exceptions;
* IDs;
* timestamps/clocks;
* serialization helpers;
* test helpers базового уровня;
* low-level logging abstractions.

---

## 16.2. Что нельзя класть в `shared/`

Нельзя тащить туда:

* бизнес-логику reminders;
* attachment policies;
* masking logic;
* snapshot transforms;
* telegram сценарии;
* rendering правила.

---

# 17. Documentation-first правила

## 17.1. В документации должна появиться новая главная карта

Обязательные документы:

### `docs/overview/system-map.md`

Короткая карта системы на 1 экран.

### `docs/architecture/runtime-vs-modules.md`

Разделение:

* entrypoint;
* runtime;
* contexts;
* infra.

### `docs/architecture/module-boundaries.md`

Что кому можно импортировать.

### `docs/architecture/command-ownership.md`

Таблица command → owning module.

### `docs/architecture/route-ownership.md`

Таблица route → owning module.

### `docs/architecture/trigger-orchestration.md`

Какие триггеры какие команды создают.

### `docs/modules/<module>.md`

Отдельный документ на каждый модуль.

---

## 17.2. Обязательное свойство документации

Документация должна описывать **текущее canonical состояние**, а не историю миграции.

История миграции — только в `archive/`.

---

# 18. Architecture fitness rules — автоматические запреты

Нужно не только описать новую архитектуру, но и **запретить её размывать**.

---

## 18.1. Проверки импортов

Нужны автоматические проверки, запрещающие:

* импорт внутренностей чужого контекста;
* импорт из `archive/` в активный runtime;
* импорт `os.getenv` вне config loader;
* импорт runtime platform кода из domain layers без нужды;
* появление новых top-level active code roots кроме `src/`.

---

## 18.2. Проверки размеров модулей

Нужны guardrails:

* entrypoint files не больше заданного порога;
* `public.py` не должен быть жирным;
* `module.py` не должен содержать бизнес-логику;
* крупные файлы помечаются как архитектурный smell.

---

## 18.3. Проверки layering

Должны быть тесты/скрипты, гарантирующие:

* `domain/` не импортирует `adapters/`;
* `domain/` не зависит от transport/runtime;
* `application/` не лазит в чужие внутренности;
* `public.py` не содержит доменной логики;
* `entrypoint/` не зависит от infra напрямую.

---

# 19. Тонкие entrypoint’ы — жёсткие шаблоны

## 19.1. Шаблон для `handler.py`

Разрешено:

* parse_request
* match/case
* lazy imports
* direct delegation

Запрещено:

* build global app
* business validation
* command decoding business-layer
* heavy logging logic inline
* direct database access
* side effects кроме delegation

---

## 19.2. Шаблон для `queue_dispatch.py`

Разрешено:

* parse envelope
* decode command envelope
* match/case по type
* lazy import owning module
* delegate

Запрещено:

* реальная бизнес-логика команд
* ручное управление всеми репозиториями всех модулей
* inline data transformation доменного уровня

---

## 19.3. Шаблон для `orchestration.py`

Разрешено:

* принять trigger
* определить orchestration plan
* enqueue команды
* вернуть accepted/status result

Запрещено:

* inline long-running business work
* прямое выполнение тяжёлых use cases
* владение доменными правилами модулей

---

# 20. Поэтапная кампания переделки

---

## Кампания 1. Зафиксировать целевую архитектуру как договор

### Цель

Прежде чем двигать код, зафиксировать канон на уровне документации и guardrails.

### Задачи

1. Создать `docs/overview/system-map.md`.
2. Создать `docs/architecture/module-boundaries.md`.
3. Создать `docs/architecture/command-ownership.md`.
4. Создать `docs/architecture/route-ownership.md`.
5. Создать `docs/architecture/trigger-orchestration.md`.
6. Создать документы модулей:

   * `docs/modules/snapshot.md`
   * `docs/modules/rendering.md`
   * `docs/modules/reminders.md`
   * `docs/modules/telegram_interaction.md`
   * `docs/modules/attachments.md`
   * `docs/modules/access_api.md`
7. Добавить раздел в README:

   * current system map;
   * where to start reading code;
   * active code only lives in `src/`.

### Критерий завершения

Любой новый разработчик может за 10 минут понять:

* какие есть модули;
* какой код считается runtime/platform;
* кто владеет какими маршрутами и командами.

---

## Кампания 2. Создать новый каркас `src/` и тонкие entrypoint’ы

### Цель

Сделать новый skeleton без переноса всей логики, но с жёсткими точками входа.

### Задачи

1. Создать:

   * `src/entrypoint/handler.py`
   * `src/entrypoint/parse_request.py`
   * `src/entrypoint/modes.py`
   * `src/entrypoint/responses.py`
2. Создать:

   * `src/platform/runtime/queue_dispatch.py`
   * `src/platform/runtime/orchestration.py`
   * `src/platform/runtime/classify.py`
3. Реализовать тонкий `handler.py` по шаблону.
4. Перенести существующую классификацию событий в новый entrypoint слой.
5. Сохранить текущие режимы:

   * http;
   * telegram webhook;
   * worker;
   * timer;
   * morning;
   * healthcheck.
6. Добавить тесты на route/mode classification.

### Критерий завершения

Открывая `handler.py`, видно всю верхнюю карту системы.

---

## Кампания 3. Ввести модульные контексты и public/module фасады

### Цель

Сделать контексты first-class citizens.

### Задачи

1. Создать каркасы:

   * `contexts/snapshot/`
   * `contexts/rendering/`
   * `contexts/reminders/`
   * `contexts/telegram_interaction/`
   * `contexts/attachments/`
   * `contexts/access_api/`
2. Для каждого создать:

   * `public.py`
   * `module.py`
   * `contracts/`
   * `application/`
   * `domain/`
   * `adapters/`
3. Создать пустые/минимальные module builders.
4. Сделать public API с минимальными функциями:

   * `handle_command`
   * `handle_http_request`
   * `handle_webhook`
   * по необходимости `query(...)`
5. Добавить архитектурные тесты, запрещающие импорт внутренних частей чужого контекста.

### Критерий завершения

Контексты существуют как реальные границы, даже если логика внутри ещё не вся перенесена.

---

## Кампания 4. Перенести ownership команд и queue dispatch

### Цель

Сделать queue flow модульным, но не сломать его.

### Задачи

1. Выделить internal command types в явный контракт.
2. Создать таблицу command ownership в коде и документации.
3. Переделать queue worker dispatch так, чтобы он:

   * парсил envelope;
   * декодировал command;
   * делегировал в owning module.
4. Убрать бизнес-логику из worker shell.
5. Добавить тесты:

   * command routing;
   * unknown command handling;
   * retries/error surfaces.

### Критерий завершения

Worker знает только transport + routing, но не все бизнес-детали.

---

## Кампания 5. Перенести trigger orchestration

### Цель

Отделить triggers от доменной логики.

### Задачи

1. Реализовать `handle_timer_trigger`.
2. Реализовать `handle_morning_trigger`.
3. Убедиться, что:

   * timer enqueue-ит snapshot + render commands;
   * morning enqueue-ит reminder command.
4. Убрать доменную логику из trigger shell.
5. Добавить integration tests на orchestration plans.

### Критерий завершения

Триггеры стали orchestration-only слоем.

---

## Кампания 6. Перенести `attachments` как отдельный модуль первого класса

### Цель

Самый сильный кандидат на самостоятельный модуль/будущий сервис должен стать архитектурно чистым.

### Задачи

1. Собрать полную карту attachment сценариев:

   * request upload;
   * direct upload;
   * finalize;
   * metadata attach;
   * preview;
   * delete;
   * cleanup;
   * read/download/view.
2. Перенести attachment routes в `contexts/attachments`.
3. Перенести attachment commands в `contexts/attachments/contracts`.
4. Ввести attachment state machine в `domain/`.
5. Перенести preview logic в `application/` + `adapters/preview_converter.py`.
6. Отделить object storage adapter.
7. Добавить модульные тесты жизненного цикла attachment.

### Критерий завершения

Attachments выглядят как почти самостоятельный subsystem, а не разбросанный набор хендлеров и jobs.

---

## Кампания 7. Перенести `reminders` как самостоятельный контекст

### Цель

Убрать смешение reminder domain, delivery и trigger semantics.

### Задачи

1. Перенести selection rules в `domain/selection_rules.py`.
2. Перенести send flow в `application/send_reminders.py`.
3. Выделить delivery gateway adapter.
4. Выделить llm styler adapter.
5. Свести retry/send counters в локальную application/business-логику.
6. Отделить reminder module от `morning` trigger semantics.
7. Добавить unit tests для selection rules и message building.

### Критерий завершения

Reminders модуль живёт сам по себе и не размазан по runtime.

---

## Кампания 8. Перенести `snapshot` и `rendering` в два отдельных модуля

### Цель

Не смешивать обновление состояния и генерацию представлений.

### Задачи

1. Зафиксировать public API `snapshot`.
2. Зафиксировать public API `rendering`.
3. Перенести snapshot update use case в `snapshot/application/`.
4. Перенести normalize/domain модели в `snapshot/domain/`.
5. Перенести render jobs в `rendering/application/`.
6. Отделить render adapters от snapshot ingestion adapters.
7. Убрать прямые глубокие связи между rendering и внутренностями snapshot.
8. Пусть rendering получает только подготовленные контракты snapshot.

### Критерий завершения

Snapshot и rendering — два разных модуля, даже если оба работают вокруг таблиц.

---

## Кампания 9. Перенести `telegram_interaction`

### Цель

Собрать Telegram interaction в единый модуль, не смешивая его с reminder domain.

### Задачи

1. Перенести webhook intake.
2. Перенести update parsing.
3. Перенести routing правил Telegram-сообщений.
4. Перенести mapping update → internal command.
5. Отделить Telegram adapter как infrastructure detail.
6. Добавить tests на webhook routing.

### Критерий завершения

Telegram взаимодействие перестаёт быть размазанным по разным слоям.

---

## Кампания 10. Перенести `access_api`

### Цель

Сделать frontend-facing surface чистым отдельным модулем.

### Задачи

1. Перенести frontend/public API handler в `contexts/access_api`.
2. Выделить access policy.
3. Выделить masking rules.
4. Выделить response shaping / DTO assembly.
5. Убедиться, что access_api не знает ingestion/render execution internals.
6. Добавить tests для masked/open режимов.

### Критерий завершения

Frontend/API surface становится самостоятельным модулем с понятным контрактом.

---

## Кампания 11. Конфигурация и среда запуска

### Цель

Сделать проект самодостаточным и предсказуемым.

### Задачи

1. Свести конфиг в `src/platform/config/loader.py`.
2. Создать typed config models.
3. Запретить `os.getenv` вне config layer.
4. Нормализовать local dev / pytest path.
5. Сделать единый documented запуск:

   * install
   * test
   * local run
6. Привести package layout к стабильному виду.

### Критерий завершения

Конфигурация и локальный запуск не требуют магических знаний.

---

## Кампания 12. Архивирование legacy и зачистка корня

### Цель

Убрать визуальную археологию из активного контура.

### Задачи

1. Перенести устаревшие куски в `archive/`.
2. Убрать из активного пути:

   * старые code roots;
   * старые compatibility wrappers;
   * legacy-only docs.
3. Обновить README и docs так, чтобы legacy не светился как часть активной системы.
4. Добавить guardrails на импорт из `archive/`.

### Критерий завершения

Репозиторий визуально выглядит как единая текущая система, а не как реконструкция истории.

---

# 21. Конкретные технические запреты

## 21.1. Нельзя

* импортировать чужие внутренности контекста;
* добавлять бизнес-логику в `entrypoint/`;
* добавлять бизнес-логику в `platform.runtime`;
* строить глобальный app container со всеми модулями;
* читать env в случайных местах;
* плодить новые top-level active packages вне `src/`;
* хранить active legacy-код вне `src/`;
* использовать `shared/` как мусоросборник;
* создавать новый “mega-bootstrap”.

---

## 21.2. Обязательно

* каждый модуль имеет `public.py`;
* каждый модуль имеет `module.py`;
* queue dispatch виден явно через `match/case`;
* entrypoint виден явно через `match/case`;
* trigger orchestration отделён от business execution;
* command ownership документирован;
* route ownership документирован;
* architecture tests защищают границы.

---

# 22. Тестовая стратегия под новую архитектуру

## 22.1. Что тестируем

### Unit

* domain rules внутри модулей;
* config parsing;
* request classification;
* command ownership mapping.

### Integration

* entrypoint routing;
* queue dispatch;
* trigger orchestration;
* attachment lifecycle;
* reminders flow;
* masked/open API mode.

### Architecture

* import boundaries;
* forbidden imports;
* layering constraints;
* no legacy usage in active path.

---

# 23. Целевой порядок чтения кода для нового разработчика

После переделки человек должен читать систему в таком порядке:

1. `README.md`
2. `docs/overview/system-map.md`
3. `src/entrypoint/handler.py`
4. `src/platform/runtime/orchestration.py`
5. `src/platform/runtime/queue_dispatch.py`
6. `docs/architecture/module-boundaries.md`
7. `docs/modules/<interesting-module>.md`
8. `src/contexts/<module>/public.py`
9. `src/contexts/<module>/module.py`
10. внутренности модуля

Если это не работает — архитектура ещё недостаточно прозрачна.

---

# 24. Definition of Done для всей переделки

Переделка считается завершённой, когда выполняются все условия:

1. Активный runtime-код живёт только в `src/`.
2. Верхняя точка входа — тонкая, явная и читаемая с одного экрана.
3. Есть явный `match/case` routing по mode.
4. Есть явный `match/case` queue dispatch по command type.
5. Trigger orchestration отделён от domain execution.
6. Есть 6 основных контекстов первого класса:

   * snapshot
   * rendering
   * reminders
   * telegram_interaction
   * attachments
   * access_api
7. Каждый контекст имеет:

   * `public.py`
   * `module.py`
   * `contracts/`
   * `application/`
   * `domain/`
   * `adapters/`
8. Глубокие cross-module imports запрещены и проверяются тестами/скриптами.
9. Legacy/old код не мешает читать активную систему.
10. Документация описывает текущее canonical устройство, а не историю хаоса.
11. Очереди, timer, morning, attachments, reminders, snapshot/render сценарии работают без потери поведения.
12. Репозиторий выглядит как целостная, современная, хорошо организованная система.

---

# 25. Краткое финальное правило проекта

Проект должен отвечать следующим принципам:

* **сначала понять режим, потом строить модуль;**
* **runtime отдельно, бизнес-модули отдельно;**
* **контексты важнее transport-слоёв;**
* **ownership явный, не угадываемый;**
* **тонкие entrypoint’ы, явный routing, ноль магии;**
* **минимум shared, минимум глобальности;**
* **границы enforced кодом и тестами;**
* **архитектура должна читаться глазами, а не восстанавливаться раскопками.**


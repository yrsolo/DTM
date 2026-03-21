```md
# FILE: work/campaigns/000-architecture-recovery/README.md

# DTM — программа архитектурного лечения

Этот набор файлов задаёт **единый канон переделки** DTM.  
Это не “ещё один рефакторинг по ощущениям” и не “косметическая чистка слоёв”.

Это программа перехода от состояния:

- архитектура существует в документации;
- ownership размазан;
- вход в систему когнитивно мутный;
- новые фасады живут рядом со старыми implementation-кластерами;

к состоянию:

- проект читается сверху вниз;
- вход реально простой;
- runtime нейтральный;
- каждый сценарий принадлежит owning module;
- межмодульные связи узкие;
- старые пути больше не считаются нормой.

## Главная цель

Сделать DTM **модульным монолитом с жёстким ownership**, где:

- верхний вход короткий и наглядный;
- `platform.runtime` владеет только runtime concerns;
- бизнес-код организован вокруг модулей первого класса;
- старые технические кластеры перестают быть архитектурными центрами;
- остаточная связанность между модулями сводится к narrow contracts, queue jobs и invalidation intents.

## Модули первого класса

Целевые owning modules:

- `snapshot`
- `rendering`
- `reminders`
- `attachments`
- `telegram_interaction`
- `access_api`

Целевой platform layer:

- `platform.runtime`

## Главный диагноз

Основная проблема не в том, что проект “недостаточно модульный”.

Основная проблема в том, что **каноническая единица организации кода до сих пор не модуль, а технический слой / исторический кластер**.

Сейчас код глазами читается через:

- entrypoints
- worker
- jobs
- services
- snapshot_engine
- telegram
- notify

А должен читаться через:

- platform.runtime
- snapshot
- rendering
- reminders
- attachments
- telegram_interaction
- access_api

## Главный принцип внедрения

Нельзя дальше лечить проект мягко, только через:
- новые фасады;
- новые обёртки;
- новые shell-слои поверх старого.

Нужно внедрять **новый канон как обязательный путь**, а старые пути:
- запрещать;
- выжигать;
- переводить в переходные зоны с явным сроком удаления.

## Как пользоваться этим набором

Порядок чтения и исполнения:

1. `docs/architecture-recovery/goals-and-principles.md`
2. `docs/architecture-recovery/target-system-map.md`
3. `docs/architecture-recovery/ownership-and-boundaries.md`
4. `docs/architecture-recovery/runtime-canon.md`
5. `docs/architecture-recovery/migration-rules.md`
6. кампании по порядку:
   - `010-freeze-the-canon.md`
   - `020-simplify-the-top-path.md`
   - `030-break-bootstrap-gravity.md`
   - `040-attachments-first-class-module.md`
   - `050-decouple-cache-through-intents.md`
   - `060-reminders-module.md`
   - `070-snapshot-rendering-split.md`
   - `080-telegram-interaction.md`
   - `090-access-api.md`
   - `100-final-structure-and-archive.md`
   - `110-guardrails-and-done.md`

## Ключевая дисциплина

Каждая кампания обязана:
- улучшать ownership;
- уменьшать количество промежуточных мостов;
- делать вход или модуль более прямым;
- убивать хотя бы один старый путь, а не оставлять его рядом;
- фиксировать запрет тестом/guardrail/documented rule.

## Что запрещено

Запрещено:
- строить новый слой красивой абстракции поверх старого ownership;
- плодить новые router/dispatcher/factory/bridge конструкции без уничтожения старого пути;
- тащить бизнес-логику в `entrypoint` и `platform.runtime`;
- продолжать считать старые technical clusters “допустимой нормой”.

## Результат, который считается успехом

Работа считается успешной, только если в конце:
- верхний путь чтения системы занимает 1–2 экрана;
- `bootstrap` перестаёт быть скрытым мозгом проекта;
- каждый сценарий запускается через один очевидный owning module;
- прямые межмодульные зависимости заменены контрактами/командами/intents;
- кэш перестаёт быть смысловой связкой модулей;
- старые implementation-кластеры либо архивированы, либо архитектурно разжалованы;
- код можно читать глазами, а не раскопками по цепочке делегаторов.
```

```md
# FILE: work/campaigns/000-architecture-recovery/docs/architecture-recovery/goals-and-principles.md

# Цели и принципы архитектурного лечения DTM

## 1. Что лечим на самом деле

Мы не лечим “неаккуратность”.
Мы не лечим “недостаток слоёв”.
Мы не лечим “нехватку документации”.

Мы лечим вот это состояние:

- новая архитектура декларируется, но не доминирует;
- ownership не совпадает с файловой организацией;
- верхний путь выполнения остаётся когнитивно мутным;
- код читается через технические кластеры, а не через доменные модули;
- старые пути продолжают жить как равноправные.

## 2. Целевое состояние

DTM должен стать **module-first system**.

Это означает:

- существует один короткий верхний вход;
- существует один небольшой runtime/platform слой;
- существуют owning modules первого класса;
- каждый сценарий принадлежит конкретному модулю;
- каждый модуль имеет один публичный вход;
- межмодульная координация идёт только через:
  - contracts;
  - commands/queries;
  - queue jobs;
  - invalidation intents;
  - runtime-owned orchestration.

## 3. Главные принципы

### 3.1. Module first
Архитектурной единицей системы является модуль, а не:
- handler;
- shell;
- worker;
- jobs package;
- services package;
- technology adapter.

### 3.2. Runtime is neutral
`platform.runtime` не владеет предметной логикой.
Он отвечает только за:
- классификацию входов;
- orchestration triggers;
- queue dispatch;
- runtime diagnostics;
- health/ops surfaces.

### 3.3. One obvious path
У каждого сценария должен быть один очевидный путь запуска:
- entrypoint
- runtime routing
- owning module public facade
- module-local builder/use case

Без лабиринта из:
- возвращающих функций;
- фабрик ради фабрик;
- слоёв совместимости без ownership.

### 3.4. No deep cross-module knowledge
Один модуль не должен знать внутренности другого.
Разрешены только:
- `public.py`
- `contracts`
- internal commands/events/intents

### 3.5. Cache is not domain glue
Кэш не считается смысловой связкой модулей.
Любая cache invalidation после мутации должна идти через:
- queue job;
- invalidation intent;
- runtime-owned cache invalidation layer.

### 3.6. Old path must die
Новый путь не считается внедрённым, пока старый путь не:
- запрещён;
- удалён;
- или не переведён в явный deprecated bridge с задачей на удаление.

## 4. Главный критерий качества

Открыв:
- entrypoint
- public facade модуля
- module builder модуля

разработчик должен за 30–60 секунд понять:
- куда попадает сценарий;
- какой модуль им владеет;
- где строятся зависимости;
- где выполняется use case.

Если это не так — рефакторинг недостаточен.

## 5. Что не является успехом

Не считаются успехом:
- новые документы без новых запретов;
- новые фасады без смерти старых путей;
- новый routing без переноса ownership;
- новый builder поверх старого megabootstrap;
- рост количества мостов, делегаторов и lazy-wrapper’ов;
- рост “формальной модульности” без улучшения читаемости.

## 6. Порядок приоритетов

Порядок важности:

1. ownership сценариев
2. простота верхнего пути
3. разгрузка bootstrap
4. прямота module entry
5. развязка кэша через intents/jobs
6. удаление старых путей
7. красота файловой структуры

Красота путей важна, но только после реальной смены ownership.
```

````md
# FILE: work/campaigns/000-architecture-recovery/docs/architecture-recovery/target-system-map.md

# Целевая карта системы

## 1. Главная форма проекта

Проект должен читаться как:

- `entrypoint`
- `platform.runtime`
- owning modules

И больше ничто не должно конкурировать с этой картой.

## 2. Целевые зоны ответственности

### 2.1. `entrypoint`
Назначение:
- принять входящее событие;
- дёшево классифицировать mode;
- передать выполнение дальше.

`entrypoint` не владеет:
- предметной логикой;
- конфигом модулей;
- бизнес-правилами;
- кэшем;
- доменными зависимостями.

### 2.2. `platform.runtime`
Назначение:
- mode classification support;
- queue dispatch;
- trigger orchestration;
- runtime observability/ops/health surfaces;
- status/intake runtime concerns.

`platform.runtime` не владеет:
- reminders business rules;
- attachment lifecycle;
- rendering rules;
- snapshot domain logic;
- access shaping;
- telegram interaction semantics.

### 2.3. `snapshot`
Назначение:
- ingestion;
- normalization;
- snapshot update;
- prepared snapshot queries.

### 2.4. `rendering`
Назначение:
- timeline rendering;
- designers rendering;
- output generation and writeback.

### 2.5. `reminders`
Назначение:
- selection rules;
- reminder payload building;
- styling;
- delivery use case;
- reminder-specific retries/counters if business-significant.

### 2.6. `attachments`
Назначение:
- upload contract;
- finalize;
- metadata attach;
- preview lifecycle;
- delete lifecycle;
- cleanup;
- read/download/view policy.

### 2.7. `telegram_interaction`
Назначение:
- webhook intake;
- update parsing;
- mapping update -> internal command;
- group/user interaction flows.

### 2.8. `access_api`
Назначение:
- frontend-facing HTTP contract;
- masked/open access behavior;
- response shaping;
- access policy.

## 3. Что не является модулями первого класса

Следующие зоны не должны считаться самостоятельными бизнес-модулями:

- `jobs`
- `worker`
- `services`
- `notify`
- `telegram` как pure technology package
- `snapshot_engine` как giant internal cluster
- `http handlers` как доменные центры

Это либо:
- runtime;
- infrastructure;
- historical implementation clusters;
- transition zones.

## 4. Целевой путь чтения системы

Нормальный путь чтения кода:

1. `entrypoint/handler`
2. `entrypoint/parse_request`
3. `platform.runtime`
4. `contexts/<module>/public.py`
5. `contexts/<module>/module.py`
6. `contexts/<module>/application/...`
7. `contexts/<module>/domain/...`

Если для понимания сценария надо сначала пройти через:
- общий bootstrap;
- несколько shell-слоёв;
- services;
- jobs;
- historical helpers,

значит система ещё не доведена до целевой формы.

## 5. Целевая форма структуры

```text
src/
  entrypoint/
  platform/
    runtime/
    config/
    infra/
  contexts/
    snapshot/
    rendering/
    reminders/
    attachments/
    telegram_interaction/
    access_api/
  shared/
````

## 6. Нормальная форма public entry модуля

Каждый модуль должен иметь один очевидный публичный вход.
Например:

* `handle_command(...)`
* `handle_http_request(...)`
* `handle_webhook(...)`
* `query(...)`

Публичный вход:

* тонкий;
* прямой;
* не прячет ownership;
* не заставляет лазить по трем делегаторам.

## 7. Нормальная форма module builder

Каждый модуль должен собирать себя сам.
Глобальный bootstrap не должен руками собирать доменную внутренность всех модулей.

````

```md
# FILE: work/campaigns/000-architecture-recovery/docs/architecture-recovery/ownership-and-boundaries.md

# Ownership и границы модулей

## 1. Основное правило

Каждый сценарий системы обязан иметь **одного owning module**.

Нельзя оставлять сценарий:
- между runtime и jobs;
- между http и services;
- между telegram и reminders;
- между snapshot_engine и render;
- между access handlers и internal query code.

## 2. Ownership-карта верхнего уровня

### `platform.runtime`
Владеет:
- queue transport
- trigger orchestration
- intake classification
- healthcheck
- runtime diagnostics
- queue/status/ops surfaces, если они не являются бизнес-API

### `snapshot`
Владеет:
- update snapshot
- normalized state preparation
- snapshot queries

### `rendering`
Владеет:
- render timeline
- render designers
- generation of output representations

### `reminders`
Владеет:
- send reminders
- build reminder payloads
- reminder selection logic
- reminder styling/delivery

### `attachments`
Владеет:
- request upload
- finalize upload
- attach metadata
- generate preview
- delete attachment
- cleanup stale attachments
- read/download/view attachment policy

### `telegram_interaction`
Владеет:
- telegram webhook processing
- group query reply
- update routing
- user/group interaction scenarios

### `access_api`
Владеет:
- frontend-facing API contract
- masked/open access output
- browser-safe response shaping

## 3. Особые ownership-решения

### 3.1. `group_query_reply`
Закрепить ownership за `telegram_interaction`.

Он не должен оставаться:
- сиротой;
- абстрактной queue-командой без модуля;
- hidden feature внутри runtime.

### 3.2. Cache invalidation
Не принадлежит модулям как cross-module knowledge.
Модуль может:
- публиковать invalidation intent;
- enqueue invalidation job;
- вернуть mutation aftermath metadata.

Но модуль не должен:
- напрямую чистить кэш чужого модуля;
- знать cache internals чужого API surface.

## 4. Boundary rules

### 4.1. Разрешённые межмодульные зависимости
Разрешено:
- `contexts.other.public`
- `contexts.other.contracts`
- queue command contracts
- invalidation intents
- narrow query/command interfaces

### 4.2. Запрещённые межмодульные зависимости
Запрещено:
- импорт чужого `application`
- импорт чужого `domain`
- импорт чужого `adapters`
- импорт внутренних engine/service helper’ов чужого модуля

## 5. Особый boundary: `snapshot` -> `rendering`

Это один из важнейших швов.

`rendering` может зависеть только от:
- `snapshot.public`
- `snapshot.contracts`

`rendering` не может зависеть от:
- `snapshot_engine` internals
- snapshot repositories
- internal normalized objects not exported as contracts
- source ingestion details

## 6. Особый boundary: `attachments` -> `access_api`

`attachments` не должен знать:
- access response shaping
- browser cache details
- HTTP route composition access layer

`access_api` не должен знать:
- attachment internal lifecycle state machine
- preview generation internals
- storage implementation details

Связь только через:
- narrow read/query contracts
- invalidation intents / queue jobs

## 7. Признак неправильной границы

Граница считается плохой, если:
- без reading internal file другого модуля сценарий непонятен;
- нужно прокинуть engine/service object наружу;
- runtime знает domain-specific builders;
- кэш чистится “руками” модуля в чужой зоне;
- один и тот же business flow размазан по нескольким technical packages.
````

```md
# FILE: work/campaigns/000-architecture-recovery/docs/architecture-recovery/runtime-canon.md

# Канон верхнего пути выполнения

## 1. Цель

Верхний путь выполнения должен быть:
- коротким;
- очевидным;
- дешёвым по инициализации;
- когнитивно прямым.

Не допускается ситуация, когда вход технически “тонкий”, но глазами читается как лабиринт из getter’ов, lazy-wrapper’ов и делегаторов.

## 2. Целевой стиль entrypoint

### 2.1. Нормальный верхний `handler`
- принимает событие
- вызывает `parse_request`
- делает явный `match/case` по mode
- импортирует owning handler lazily
- делегирует выполнение

### 2.2. Что должно быть видно глазами
В одном месте должно быть видно:
- какие mode существуют
- куда ведёт каждый mode
- где runtime path
- где module path

## 3. Что считается недопустимым

Недопустимы:
- registry-магия, скрывающая путь;
- dispatch через малоочевидные таблицы и factories;
- functions returning functions ради архитектурной красоты;
- несколько уровней get_* / build_* / create_* на основном пути чтения;
- top-level path, который нельзя понять за 1 экран.

## 4. Целевой runtime path

### 4.1. HTTP / external event
`entrypoint` -> `platform.runtime or module public facade`

### 4.2. Queue path
`entrypoint` -> `platform.runtime.queue_dispatch` -> `contexts.<owner>.public.handle_command`

### 4.3. Trigger path
`entrypoint` -> `platform.runtime.orchestration` -> enqueue domain-owned commands

## 5. Правила для `platform.runtime`

Разрешено:
- parse queue envelope
- decode command
- mode classification
- runtime status/health
- orchestration of trigger fan-out
- telemetry wrappers уровня runtime

Запрещено:
- строить доменные зависимости модулей;
- знать domain-specific implementation clusters;
- владеть business logic модулей;
- напрямую управлять domain use cases вместо модулей.

## 6. Правила для queue dispatch

Queue dispatch обязан быть:
- явным;
- ownership-based;
- читаемым глазами.

Никакой магии.
Предпочтителен `match/case` по command type.

## 7. Правила для trigger orchestration

Trigger orchestration обязан:
- собирать только orchestration plan;
- испускать команды;
- не выполнять тяжёлую доменную работу inline.

## 8. Признак успеха

Если новый разработчик открывает верхний путь и сразу понимает:
- где runtime
- где модули
- кто владеет сценарием

значит канон соблюдён.
```

```md
# FILE: work/campaigns/000-architecture-recovery/docs/architecture-recovery/migration-rules.md

# Правила миграции

## 1. Общий подход

Миграция выполняется не как “косметическая чистка”, а как **замена канона**.

Каждый шаг обязан:
- вводить новый обязательный путь;
- переводить ownership в модуль;
- убивать или ограничивать старый путь;
- закреплять результат тестом или guardrail’ом.

## 2. Сначала смысл, потом география

Нельзя начинать с массового переноса файлов ради красивой структуры.

Сначала:
- ownership;
- public facade;
- local module builder;
- routing;
- guardrail.

Потом:
- физический перенос файлов;
- archive cleanup;
- окончательная география папок.

## 3. Один модуль за раз

Не надо пытаться довести до идеала сразу все контексты.
Нужно работать по одному:

1. attachments
2. reminders
3. snapshot/rendering boundary
4. telegram_interaction
5. access_api

## 4. Старые мосты допустимы только как переходные

Переходный bridge допустим только если:
- он короткий;
- он явно помечен;
- у него есть задача на удаление;
- он не становится новой нормой.

## 5. Любой новый код обязан жить по новому канону

Запрещено писать новый код:
- в старые technical clusters как в нормальное место развития;
- мимо public facade owning module;
- через старый bootstrap, если уже существует module builder.

## 6. Любая новая мутация обязана оформлять aftermath явно

После мутации модуль обязан:
- либо вернуть invalidation intent;
- либо enqueue invalidation job;
- либо публиковать internal mutation aftermath metadata.

Запрещено:
- напрямую трогать чужой кэш;
- напрямую вызывать чужие internal cache services.

## 7. Документация обновляется в каждой кампании

После каждой кампании обязательно обновить:
- ownership table
- route ownership
- command ownership
- deprecated paths
- module docs

## 8. Критерий хорошей кампании

Кампания хорошая, если:
- ownership стал яснее;
- путь чтения стал короче;
- старый путь ослаблен или убит;
- добавлен guardrail;
- новый разработчик видит меньше технического шума.
```

```md
# FILE: work/campaigns/000-architecture-recovery/010-freeze-the-canon.md

# Кампания 010 — зафиксировать канон и запретить дальнейшее расползание

## Цель

Прежде чем что-либо переносить, зафиксировать:
- новый канон системы;
- ownership сценариев;
- boundary rules;
- migration rules;
- первые запреты.

Без этого любая дальнейшая работа снова сведётся к мягким полумерам.

## Что сделать

### 1. Добавить документацию архитектурного лечения
Создать и заполнить:

- `work/campaigns/000-architecture-recovery/docs/architecture-recovery/goals-and-principles.md`
- `work/campaigns/000-architecture-recovery/docs/architecture-recovery/target-system-map.md`
- `work/campaigns/000-architecture-recovery/docs/architecture-recovery/ownership-and-boundaries.md`
- `work/campaigns/000-architecture-recovery/docs/architecture-recovery/runtime-canon.md`
- `work/campaigns/000-architecture-recovery/docs/architecture-recovery/migration-rules.md`

### 2. Зафиксировать ownership-таблицы
Создать и заполнить:

- `docs/architecture/module-boundaries.md`
- `docs/architecture/command-ownership.md`
- `docs/architecture/route-ownership.md`
- `docs/architecture/trigger-orchestration.md`

### 3. Закрепить важные ownership-решения
Явно зафиксировать:
- `group_query_reply` принадлежит `telegram_interaction`
- cache invalidation не является доменной связкой между модулями
- `rendering` не имеет права читать internal snapshot engine state напрямую

### 4. Добавить минимальные ранние guardrails
Добавить проверку/тесты на:
- запрет deep imports во внутренности чужого модуля
- запрет новых импортов из legacy/archive в активный путь
- запрет новых `os.getenv` вне config layer
- запрет развития top-level routing через новые скрытые dispatch abstractions
- запрет прямых cross-module cache calls

## Что не делать
- не переносить массово файлы
- не реорганизовывать всё дерево
- не переписывать сейчас половину проекта
- не пытаться сразу “довести до идеала”

## Результат
Появляется единый договор, после которого:
- понятно, что считается правильным;
- понятно, что теперь нельзя;
- дальнейшие кампании не спорят о базовой архитектурной модели.

## Definition of Done
Кампания завершена, если:
- документы созданы и согласованы;
- ownership-таблицы заполнены;
- boundary rules записаны;
- минимум 3–5 guardrails работают в CI/локально;
- новые изменения уже нельзя делать “по старинке” без срабатывания запретов.

## После завершения прочитать
- `020-simplify-the-top-path.md`
- `docs/architecture-recovery/runtime-canon.md`
```

```md
# FILE: work/campaigns/000-architecture-recovery/020-simplify-the-top-path.md

# Кампания 020 — упростить верхний путь выполнения до реально понятного вида

## Цель

Сделать вход в систему таким, чтобы его можно было понять глазами без раскопок.

Сейчас верхний путь слишком технический:
- ленивые getter’ы;
- обёртки;
- диспетчеры;
- shell-цепочки;
- лишние уровни делегирования.

Нужно получить:
- один короткий entrypoint;
- один дешёвый parse/classify step;
- явный routing по mode;
- понятный runtime/module split.

## Что сделать

### 1. Нормализовать entrypoint
Создать или довести до канона:

- `src/entrypoint/handler.py`
- `src/entrypoint/parse_request.py`
- `src/entrypoint/modes.py`
- `src/entrypoint/responses.py`

### 2. Сделать верхний path явным
`handler.py` должен делать только:
- parse request
- `match/case` по `Mode`
- lazy import owning target
- return delegation result

### 3. Убрать лишние промежуточные уровни
Сократить или убрать:
- возвращающие функции на верхнем пути
- registry/dispatch конструкции, скрывающие маршрут
- служебные wrapper’ы, не дающие архитектурной пользы

### 4. Развести runtime surfaces и module surfaces
На верхнем routing-уровне явно показать:
- что относится к `platform.runtime`
- что относится к `contexts/*`

### 5. Нормализовать platform-owned surfaces
Явно обработать в runtime-ветках:
- healthcheck
- queue worker entry
- trigger entry
- info/admin ops surfaces, если они platform-owned

## Что не делать
- не строить глобальный app context в handler
- не тащить доменные импорты наверх
- не внедрять магический registry ради “красоты”
- не переводить все хендлеры в новый контур сразу

## Технические задачи

1. Вынести mode parsing в один дешёвый модуль.
2. Зафиксировать список mode как enum/typed object.
3. Переписать верхний routing в явный `match/case`.
4. Свести HTTP/worker/trigger входы к прозрачным runtime/module точкам.
5. Уменьшить число звеньев на top-level path.
6. Добавить тесты на mode classification и top-level routing.

## Критерии качества

Проверка глазами:
- открываешь `handler.py`
- сразу видишь карту системы
- сразу понимаешь, куда идёт queue path
- сразу понимаешь, куда идёт trigger path
- сразу понимаешь, где module public entry

Если вход всё ещё читается как инфраструктурный квест — кампания не завершена.

## Definition of Done
Кампания завершена, если:
- `handler.py` занимает примерно 1 экран;
- маршруты mode видны явно;
- количество top-level мостов уменьшено;
- нет скрытых registry-path’ов;
- добавлены тесты на mode classification и top routing;
- код entrypoint стал проще читать глазами, а не только проще формально.

## После завершения прочитать
- `030-break-bootstrap-gravity.md`
- `docs/architecture-recovery/runtime-canon.md`
```

```md
# FILE: work/campaigns/000-architecture-recovery/030-break-bootstrap-gravity.md

# Кампания 030 — сломать гравитацию глобального bootstrap

## Цель

У глобального bootstrap нужно забрать роль скрытого мозга всей системы.

Пока bootstrap знает:
- domain-specific jobs;
- builders модулей;
- wiring множества несвязанных сценариев;
- config/env details для всего мира;

он остаётся настоящим центром архитектуры, даже если снаружи появились модули и фасады.

## Что сделать

### 1. Зафиксировать новый принцип сборки
Каждый owning module обязан иметь:
- `public.py`
- `module.py`
- локальный builder
- локальный config slice
- локальную сборку domain/application/adapters

### 2. Ограничить глобальный bootstrap
Глобальный bootstrap может владеть только:
- truly shared runtime infra
- config loader top-level entry
- queue/telemetry/runtime primitives

Он не должен руками собирать внутренности модулей.

### 3. Вытащить domain ownership из bootstrap
Постепенно перестать создавать в bootstrap:
- attachment jobs/use cases
- reminder jobs/use cases
- render jobs/use cases
- telegram interaction flows
- access_api domain assembly

Это должно уехать в module-local builders.

### 4. Ввести controlled transition
Пока старый bootstrap не удалён полностью:
- он может делегировать в module builder;
- он не должен получать новый domain ownership;
- все новые сценарии обязаны строиться только через owning module.

## Технические задачи

1. Создать `module.py` для всех целевых контекстов, даже если пока часть логики внутри bridge.
2. Нормализовать шаблон `get_<module>_module()` / `build_<module>()`.
3. Перевести сборку новых/изменяемых сценариев на module-local builders.
4. Начать выносить domain-specific wiring из общего bootstrap.
5. Добавить guardrail: новый domain-specific builder нельзя добавлять в global bootstrap.

## Что не делать
- не переписывать весь config до конца прямо сейчас
- не удалять весь bootstrap сразу одним большим коммитом
- не смешивать это с полной файловой миграцией

## Результат
Bootstrap перестаёт быть местом, где архитектурно “на самом деле живёт система”.

## Definition of Done
Кампания завершена, если:
- у каждого целевого контекста есть `module.py`;
- новые изменения не добавляют domain ownership в global bootstrap;
- минимум один-два реальных сценария уже собираются через module-local builder;
- зафиксирован guardrail против роста megabootstrap.

## После завершения прочитать
- `040-attachments-first-class-module.md`
- `docs/architecture-recovery/ownership-and-boundaries.md`
```

````md
# FILE: work/campaigns/000-architecture-recovery/040-attachments-first-class-module.md

# Кампания 040 — сделать `attachments` первым настоящим module-first контуром

## Почему начинаем с attachments

`attachments` — лучший кандидат на первый полноценно изолируемый контекст, потому что:

- у него уже есть отчётливый lifecycle;
- он почти самостоятельная подсистема;
- его смысловая связанность с остальным проектом относительно слабая;
- он хороший полигон для нового канона.

## Цель

Собрать весь attachment flow под один owning module:

- request upload
- finalize upload
- metadata attach
- preview generation
- delete
- cleanup
- read/download/view
- aftermath invalidation intents

## Целевая структура

```text
src/contexts/attachments/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
````

## Что сделать

### 1. Собрать ownership в одном модуле

Все attachment-related сценарии должны входить в систему через:

* `contexts.attachments.public`

### 2. Выделить contracts

Создать:

* commands
* queries
* DTO
* results
* mutation aftermath / invalidation intent models

### 3. Выделить domain

Создать и нормализовать:

* `attachment_state_machine.py`
* `preview_policy.py`
* `cleanup_policy.py`
* domain models for attachment lifecycle

### 4. Выделить application

Use cases:

* request upload
* finalize upload
* attach metadata
* generate preview
* delete
* cleanup
* read/view

### 5. Выделить adapters

Собрать инфраструктурные детали:

* object storage
* signed urls
* preview converter
* attachment repository

### 6. Перенести routes и commands ownership

Любой attachment route и attachment queue command должен идти в `attachments.public`.

### 7. Убрать knowledge leaks

`attachments` не должен напрямую знать:

* access_api response shaping
* чужие cache internals
* snapshot engine internals кроме узких контрактов, если без этого не обойтись временно

## Допустимые временные мосты

Временные bridge’и допустимы только если:

* они живут внутри нового `attachments` контекста;
* они короткие;
* помечены как deprecated;
* имеют задачу на удаление.

## Обязательные тесты

* state machine lifecycle tests
* finalize/delete/cleanup integration tests
* preview generation tests
* read/view policy tests
* routing tests: attachment commands/routes идут только в attachments module

## Что убить по итогам

После кампании должны быть ослаблены или сняты с архитектурного пьедестала старые attachment-related центры, если они были разбросаны по:

* entrypoints
* jobs
* services
* cache helpers

## Definition of Done

Кампания завершена, если:

* attachment flow читается через один module-first контур;
* у attachments есть свой module builder;
* routes/commands ownership переехал внутрь модуля;
* старые пути больше не являются нормальным местом развития;
* cache aftermath больше не оформляется как прямое cross-module knowledge.

## После завершения прочитать

* `050-decouple-cache-through-intents.md`
* `060-reminders-module.md`

````

```md
# FILE: work/campaigns/000-architecture-recovery/050-decouple-cache-through-intents.md

# Кампания 050 — развязать модули через invalidation intents и queue jobs

## Цель

Сделать partial cache invalidation внешним aftermath-механизмом, а не смысловой склейкой модулей.

Если межмодульная связанность в основном держится на кэше, это хороший знак:
- домены уже почти независимы;
- нужно только убрать неправильную форму координации.

## Основной принцип

После мутации модуль:
- не чистит напрямую чужой кэш;
- не знает cache internals другого модуля;
- не вызывает чужой internal cache service.

Вместо этого он:
- публикует invalidation intent;
- и/или enqueue-ит invalidation job;
- и/или возвращает mutation aftermath metadata.

## Что сделать

### 1. Описать cache invalidation intents
Ввести модель внутренних invalidation intents.
Например:
- invalidate task views
- invalidate attachment views
- invalidate dashboard fragments
- invalidate snapshot-derived read models

### 2. Ввести runtime-owned invalidation handling
Реализация invalidation должна жить в:
- runtime layer
- или отдельном cache invalidation component, не принадлежащем модулям предметной области

### 3. Перевести межмодульные cache calls на intents/jobs
Заменить прямые cross-module invalidation-вызовы на:
- queue jobs
- intents
- runtime aftermath processing

### 4. Обновить ownership-документацию
Явно описать:
- какие модули публикуют какие aftermath intents;
- кто эти intents исполняет;
- какие кэши считаются runtime/cache concern, а не модульным API.

## Технические задачи

1. Создать типы invalidation intents.
2. Найти прямые cross-module cache clearing места.
3. Для каждого такого места сделать migration path:
   - old direct call -> new intent/job
4. Добавить runtime handler для invalidation jobs/intents.
5. Добавить тесты на:
   - intent emission
   - invalidation dispatch
   - отсутствие прямых чужих cache calls

## Что не делать
- не делать тяжёлую event platform
- не строить полноценную enterprise bus архитектуру
- не смешивать invalidation layer с domain ownership

## Результат
Кэш перестаёт быть аргументом за связанность модулей и превращается в инфраструктурный aftermath.

## Definition of Done
Кампания завершена, если:
- прямые cross-module cache calls исчезли или сведены к минимуму с задачей на удаление;
- мутации публикуют aftermath в виде intents/jobs;
- invalidation обрабатывается вне owning modules;
- документация обновлена.

## После завершения прочитать
- `060-reminders-module.md`
- `070-snapshot-rendering-split.md`
````

````md
# FILE: work/campaigns/000-architecture-recovery/060-reminders-module.md

# Кампания 060 — собрать `reminders` в самостоятельный owning module

## Цель

Сделать `reminders` настоящим модулем, а не размазанной смесью:
- selection logic
- delivery
- notification helpers
- telegram-adjacent behavior
- runtime trigger semantics

## Что должно войти в reminders

- selection rules
- reminder payload building
- styling
- send reminder use case
- reminder delivery orchestration
- module-local retry/counter policy, если бизнес-значимо

## Что не должно входить в reminders

- trigger `morning` как runtime source
- generic queue plumbing
- telegram webhook intake
- чужой cache invalidation implementation

## Целевая структура

```text
src/contexts/reminders/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
````

## Что сделать

### 1. Выделить public facade

Любой reminder command должен идти через:

* `contexts.reminders.public.handle_command`

### 2. Выделить domain

Создать:

* selection rules
* message models
* reminder policies

### 3. Выделить application

Use cases:

* build payloads
* send reminders
* fallback behavior
* retry/counter flow if business-owned

### 4. Выделить adapters

Собрать:

* delivery gateway
* llm styler
* reminder repo/state adapter if needed

### 5. Убрать смешение с telegram/webhook/runtime

`morning` должен остаться runtime trigger orchestration.
Telegram webhook должен жить в `telegram_interaction`.

### 6. Перевести старые notification-centric пути в owning module

Где бы раньше ни лежал reminder flow:

* `notify`
* `jobs`
* helpers
* services

архитектурно развивать его теперь можно только через `contexts/reminders`.

## Обязательные тесты

* selection tests
* payload building tests
* send flow tests
* fallback tests without styling
* retry/counter tests if kept in module
* routing tests: reminder command ownership

## Definition of Done

Кампания завершена, если:

* reminder flow читается как отдельный модуль;
* `morning` больше не воспринимается как часть reminder domain;
* telegram и reminders разделены по ownership;
* старые notify-centric implementation clusters перестали быть главным местом развития.

## После завершения прочитать

* `070-snapshot-rendering-split.md`
* `080-telegram-interaction.md`

````

```md
# FILE: work/campaigns/000-architecture-recovery/070-snapshot-rendering-split.md

# Кампания 070 — жёстко разделить `snapshot` и `rendering`

## Почему это критично

Это один из самых рискованных швов системы.

Если `rendering` продолжает знать внутренности `snapshot_engine`, то на бумаге у нас два модуля, а по факту — один большой спаянный кластер.

## Цель

Получить два разных owning modules:

- `snapshot`
- `rendering`

с узким anti-corruption boundary между ними.

## Целевой boundary

`rendering` может зависеть только от:
- `snapshot.public`
- `snapshot.contracts`

`rendering` не может зависеть от:
- snapshot engine internals
- snapshot repositories
- normalization internals
- source adapters
- internal models, не экспортируемые как contracts

## Что сделать

### 1. Нормализовать `snapshot`
Собрать в модуль:
- snapshot update
- normalization
- prepared query contracts
- snapshot repos/adapters

### 2. Нормализовать `rendering`
Собрать в модуль:
- render timeline
- render designers
- generation/writeback use cases
- render-specific adapters

### 3. Ввести narrow contracts
Определить, что именно `rendering` получает от `snapshot`:
- queries
- DTO
- prepared read models
- nothing more

### 4. Убрать прямые зависимости
Найти и убрать прямые импорты/доступ к snapshot internals из rendering-related кода.

### 5. Закрепить boundary тестами
Добавить architecture tests, запрещающие `rendering` лезть в snapshot internals.

## Технические задачи

1. Создать `contexts/snapshot/public.py` и `module.py`, если ещё не доведены.
2. Создать `contexts/rendering/public.py` и `module.py`, если ещё не доведены.
3. Вынести snapshot contracts.
4. Вынести rendering contracts.
5. Перевести render queue commands на ownership через `rendering.public`.
6. Перевести update snapshot command на ownership через `snapshot.public`.
7. Добавить anti-corruption boundary tests.

## Что не делать
- не оставлять “временный доступ к engine” как молчаливую норму
- не смешивать одновременно полный визуальный reorder файлов и boundary migration

## Definition of Done
Кампания завершена, если:
- update snapshot и render flows принадлежат разным модулям;
- `rendering` получает только узкий контракт от `snapshot`;
- прямые internal snapshot reads из rendering запрещены;
- boundary закреплён тестами и документацией.

## После завершения прочитать
- `080-telegram-interaction.md`
- `090-access-api.md`
````

````md
# FILE: work/campaigns/000-architecture-recovery/080-telegram-interaction.md

# Кампания 080 — выделить `telegram_interaction` как first-class модуль

## Цель

Собрать Telegram interaction flows в самостоятельный модуль и перестать размазывать их между:
- webhook handlers
- queue commands
- reminders
- runtime/service helpers

## Что должно принадлежать telegram_interaction

- webhook intake
- update parsing
- update routing
- mapping update -> internal command
- group/user interaction flows
- `group_query_reply`

## Что не должно принадлежать telegram_interaction

- reminder selection logic
- reminder delivery domain
- generic queue/runtime logic
- чужие access response rules

## Целевая структура

```text
src/contexts/telegram_interaction/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
````

## Что сделать

### 1. Закрепить ownership `group_query_reply`

Это обязательное решение.

### 2. Выделить public facade

Webhook и telegram commands должны идти через:

* `contexts.telegram_interaction.public`

### 3. Выделить domain/application

* update models
* routing rules
* mapping to internal commands
* group reply flow

### 4. Выделить adapters

* telegram update parser
* telegram sender
* transport-specific helpers, если нужны

### 5. Развести ownership с reminders

Telegram interaction может инициировать или триггерить reminder-related процессы, но не владеет reminder domain.

## Обязательные тесты

* webhook parse/routing
* unsupported update behavior
* `group_query_reply` ownership routing
* interaction flow tests

## Definition of Done

Кампания завершена, если:

* telegram interaction читается как отдельный модуль;
* `group_query_reply` больше не сирота;
* webhook path понятен через owning module;
* reminders и telegram разделены по ownership.

## После завершения прочитать

* `090-access-api.md`
* `100-final-structure-and-archive.md`

````

```md
# FILE: work/campaigns/000-architecture-recovery/090-access-api.md

# Кампания 090 — собрать `access_api` как настоящий внешний owning module

## Проблема

Очень часто frontend/API слой остаётся не модулем, а просто ярлыком над набором HTTP handlers.

Нужно избежать этого и сделать `access_api` настоящим owning module для внешнего API-контракта.

## Цель

Собрать в `access_api`:

- frontend-facing HTTP contract
- masked/open behavior
- access policy
- response shaping
- browser-safe DTO

## Что не должно находиться в access_api

- snapshot ingestion
- render internals
- attachment lifecycle internals
- reminder domain rules
- generic runtime intake logic

## Целевая структура

```text
src/contexts/access_api/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
````

## Что сделать

### 1. Выделить public facade

HTTP path, принадлежащий external frontend/API, должен входить через:

* `contexts.access_api.public.handle_http_request`

### 2. Выделить domain/application

* access policy
* masking rules
* response shape assembly
* browser-safe DTO contracts

### 3. Развести с internal modules

`access_api` должен получать данные только через:

* contracts
* public queries других модулей

Никаких прямых чтений internal engine/service state.

### 4. Развести с cache handling

Прямое cross-module cache управление не должно жить в access_api.
Только через runtime-owned invalidation handling.

## Обязательные тесты

* masked mode
* open mode
* response shape tests
* ownership routing tests
* no direct internal module access checks if possible

## Definition of Done

Кампания завершена, если:

* access_api стал модулем, а не просто транспортным слоем;
* response shaping и access policy принадлежат ему;
* он не лезет во внутренности других модулей;
* HTTP surface читается как owning module, а не как хаотичный набор handlers.

## После завершения прочитать

* `100-final-structure-and-archive.md`
* `110-guardrails-and-done.md`

````

```md
# FILE: work/campaigns/000-architecture-recovery/100-final-structure-and-archive.md

# Кампания 100 — финальная нормализация структуры и архивирование старых центров

## Цель

Только после переноса ownership и module builders привести географию проекта в соответствие с реальной архитектурой.

До этого момента нельзя делать массовый move-only рефакторинг ради красоты.

## Что сделать

### 1. Нормализовать active structure
Привести активный код к форме:

```text
src/
  entrypoint/
  platform/
    runtime/
    config/
    infra/
  contexts/
    snapshot/
    rendering/
    reminders/
    attachments/
    telegram_interaction/
    access_api/
  shared/
````

### 2. Разжаловать старые architectural centers

Старые technical clusters должны:

* либо исчезнуть;
* либо уйти в `archive/`;
* либо стать внутренними implementation-деталями конкретного модуля;
* либо быть явно помечены как переходные и неразвиваемые.

### 3. Архивировать historical/legacy пути

Вынести в `archive/` всё, что:

* больше не считается active architectural path;
* хранится только ради истории;
* не является нормой для дальнейшей разработки.

### 4. Обновить README и architecture docs

README и главные архитектурные документы должны показывать:

* только новую карту системы;
* только active code reading path;
* только новый канон.

## Что не делать

* не оставлять старые directories как “ещё один допустимый способ”
* не поддерживать бесконечно два равноправных способа читать код

## Технические задачи

1. Перенести/собрать remaining active code в целевые contexts/platform.
2. Обновить импорты.
3. Обновить docs navigation.
4. Отразить deprecated/archived zones.
5. Добавить guardrail: нельзя развивать archived paths.

## Definition of Done

Кампания завершена, если:

* активная структура проекта соответствует целевой карте;
* README ведёт только в новый канон;
* старые technical clusters перестали быть архитектурно значимыми;
* новый разработчик больше не видит в корне конкурирующие центры системы.

## После завершения прочитать

* `110-guardrails-and-done.md`
* `docs/architecture-recovery/target-system-map.md`

````

```md
# FILE: work/campaigns/000-architecture-recovery/110-guardrails-and-done.md

# Кампания 110 — финальные guardrails, критерии завершения и удержание канона

## Цель

Защитить новую архитектуру от обратного сползания.

После этой кампании система должна не просто “стать чище”, а получить защиту от возврата к:
- скрытому megabootstrap;
- deep cross-module imports;
- growth of technical clusters as architectural centers;
- direct cache coupling;
- мутному верхнему пути.

## Что сделать

### 1. Добавить architecture tests / scripts
Нужны проверки на:

- запрет deep imports в чужие `application/domain/adapters`
- запрет импорта из archived/legacy paths в active runtime
- запрет `os.getenv` вне config layer
- запрет прямых cross-module cache calls
- запрет роста global bootstrap domain ownership
- запрет `rendering` -> snapshot internals
- запрет нового развития старых technical clusters как active canonical paths

### 2. Добавить structural size/style checks
Нужны checks, чтобы:
- `entrypoint/handler.py` оставался коротким
- `public.py` модулей оставался тонким
- `module.py` не становился новой свалкой предметной логики
- runtime files не пухли бесконтрольно

### 3. Зафиксировать contribution rules
Обновить developer-facing правила:
- куда класть новый сценарий
- как вводить новый module-local builder
- как оформлять aftermath intents
- как делать межмодульное взаимодействие
- что считается forbidden shortcut

### 4. Обновить финальные документы
Обязательные финальные документы:
- architecture current state
- route ownership
- command ownership
- module map
- deprecated paths list

## Финальный definition of done для всей программы

Программа считается завершённой, если выполняются все условия:

1. Верхний путь чтения системы короткий и понятный.
2. `platform.runtime` не владеет предметной логикой.
3. `bootstrap` перестал быть скрытым центром мира.
4. Каждый основной сценарий имеет owning module.
5. `attachments`, `reminders`, `snapshot`, `rendering`, `telegram_interaction`, `access_api` существуют как first-class contexts.
6. `rendering` не зависит от snapshot internals.
7. Межмодульная cache-связка вынесена в intents/jobs/runtime invalidation.
8. Старые technical clusters больше не воспринимаются как архитектурные центры.
9. Active code map соответствует README и docs.
10. Guardrails не дают откатиться назад.

## Финальная проверка качества

Открыть последовательно:
- `src/entrypoint/handler.py`
- `src/platform/runtime/queue_dispatch.py`
- `src/platform/runtime/orchestration.py`
- `src/contexts/attachments/public.py`
- `src/contexts/attachments/module.py`
- `src/contexts/reminders/public.py`
- `src/contexts/snapshot/public.py`
- `src/contexts/rendering/public.py`
- `src/contexts/telegram_interaction/public.py`
- `src/contexts/access_api/public.py`

И ответить на вопросы:

1. Я вижу ли карту системы без археологии?
2. Ясно ли, кто владеет сценарием?
3. Есть ли один очевидный путь запуска?
4. Стало ли меньше мостов и возвращающих функций на пути чтения?
5. Старые пути реально умерли или хотя бы разжалованы?

Если хотя бы на два вопроса ответ “нет”, архитектурное лечение не завершено.

## После завершения обязательно прочитать
- `README.md`
- `docs/architecture/module-boundaries.md`
- `docs/architecture/command-ownership.md`
- `docs/architecture/route-ownership.md`
- `docs/architecture/trigger-orchestration.md`
- `work/campaigns/000-architecture-recovery/docs/architecture-recovery/goals-and-principles.md`
````

```md
# FILE: work/campaigns/000-architecture-recovery/agent-instructions.md

# Инструкции агенту на внедрение архитектурного лечения DTM

Работай по этим правилам без самовольной подмены цели.

## 1. Главная задача

Не “улучшить код вообще”, а перевести DTM на module-first архитектуру, где:
- вход в систему реально читаемый;
- runtime нейтрален;
- ownership сценариев принадлежит модулям;
- старые technical clusters перестают быть архитектурно значимыми;
- межмодульная координация оформляется через contracts, commands, intents и runtime-owned invalidation.

## 2. Чего не делать

Запрещено:
- делать очередной красивый слой поверх старого ownership;
- плодить новые dispatch abstractions, если они скрывают маршрут;
- вводить registry/plugin magic вместо явного routing;
- развивать старые technical clusters как будто это новая норма;
- добавлять domain-specific wiring в global bootstrap;
- делать массовый move-only рефакторинг раньше времени;
- сохранять старые пути как равноправные без пометки и плана удаления.

## 3. Что делать обязательно

Обязательно:
- работать по кампаниям в заданном порядке;
- после каждой кампании фиксировать ownership, docs и tests;
- убивать хотя бы один старый путь;
- вводить guardrails как можно раньше;
- каждый новый сценарий оформлять только через owning module.

## 4. Как принимать решения

Если есть выбор между:
- “архитектурно красиво, но мутно глазами”
- “чуть проще технически, но очевидно глазами”

предпочитай второе.

В DTM важнее:
- наглядность;
- ownership;
- прямой путь чтения;
чем абстракция ради абстракции.

## 5. Как оформлять новые модули

Каждый модуль обязан иметь:
- `public.py`
- `module.py`
- `contracts/`
- `application/`
- `domain/`
- `adapters/`

`public.py`:
- тонкий;
- только публичный вход;
- без предметной логики.

`module.py`:
- локальная сборка зависимостей;
- без превращения в новую свалку логики.

## 6. Как оформлять межмодульные связи

Разрешены:
- `public.py`
- contracts
- queue commands
- invalidation intents
- narrow queries

Запрещены:
- direct internal imports
- engine leakage
- cross-module service calls to internals
- direct foreign cache manipulation

## 7. Как оформлять aftermath после мутаций

Если после мутации нужен побочный эффект для внешних представлений:
- не дергай чужой кэш напрямую;
- публикуй invalidation intent или queue job;
- отдавай runtime/cache layer право решать, что именно чистить.

## 8. Как проверять качество шага

После каждой кампании проверяй:

1. ownership стал яснее?
2. путь чтения стал короче?
3. старый путь умер или ослаблен?
4. новый guardrail появился?
5. код стал проще глазами?

Если нет — шаг не закончен.

## 9. Основной operational порядок

Строго следуй порядку:

1. `010-freeze-the-canon.md`
2. `020-simplify-the-top-path.md`
3. `030-break-bootstrap-gravity.md`
4. `040-attachments-first-class-module.md`
5. `050-decouple-cache-through-intents.md`
6. `060-reminders-module.md`
7. `070-snapshot-rendering-split.md`
8. `080-telegram-interaction.md`
9. `090-access-api.md`
10. `100-final-structure-and-archive.md`
11. `110-guardrails-and-done.md`

Не перепрыгивай порядок без крайней причины.

## 10. Когда считать работу успешной

Успех — это не “модульность стала на 20% лучше”.
Успех — это когда проект можно читать сверху вниз, а ownership больше не скрыт за техническими кластерами и мостами.
```

```md
# FILE: work/campaigns/000-architecture-recovery/checklists/after-each-campaign.md

# Чеклист после каждой кампании

## 1. Ownership
- Стало ли понятнее, какой модуль владеет сценарием?
- Убрали ли хотя бы один ambiguous ownership zone?
- Обновили ли ownership docs?

## 2. Верхний путь чтения
- Стал ли путь до owning module короче?
- Уменьшилось ли число делегаторов?
- Уменьшилось ли число “функций, возвращающих функции” на основном path?

## 3. Старые пути
- Ослаблен ли хотя бы один старый path?
- Помечен ли deprecated bridge, если он остался?
- Есть ли задача/комментарий на удаление старого моста?

## 4. Guardrails
- Добавлен ли новый запрет или тест?
- Может ли old style снова прорасти без fail в тестах/скриптах?

## 5. Документация
- Обновлены ли module boundaries?
- Обновлены ли command/route ownership?
- Зафиксированы ли новые deprecated zones?

## 6. Визуальная читаемость
- Можно ли теперь за 30–60 секунд понять сценарий глазами?
- Стало ли меньше когнитивного шума?

Если минимум на 4 из 6 пунктов ответ “нет”, кампания не должна считаться завершённой.
```

```md
# FILE: work/campaigns/000-architecture-recovery/checklists/final-review.md

# Финальный архитектурный ревью-чеклист

## 1. Верх системы
- `handler.py` короткий и понятный
- mode-routing явный
- runtime surfaces и module surfaces разведены
- нет скрытой routing-магии

## 2. Runtime
- queue dispatch ownership-based
- trigger orchestration не владеет доменной логикой
- platform-owned surfaces определены явно
- runtime не стал новым application god layer

## 3. Bootstrap
- bootstrap не владеет доменными сборками
- module-local builders существуют
- global bootstrap не растёт domain-specific wiring’ом

## 4. Modules
- attachments first-class
- reminders first-class
- snapshot first-class
- rendering first-class
- telegram_interaction first-class
- access_api first-class

## 5. Boundaries
- rendering не знает snapshot internals
- modules общаются через public/contracts
- нет deep cross-module imports
- cache coupling вынесен в intents/jobs

## 6. Legacy and structure
- активная карта проекта соответствует docs
- historical clusters разжалованы или архивированы
- новый разработчик не видит конкурирующие архитектурные центры

## 7. Main quality question
Если открыть 5–10 ключевых файлов, становится ли понятно:
- как запускается система?
- кто владеет сценарием?
- где строятся зависимости?
- где выполняется use case?

Если нет — архитектурное лечение не доведено до конца.
```

```md
# FILE: work/campaigns/000-architecture-recovery/implementation-order.md

# Порядок внедрения

## Обязательный порядок

1. Freeze canon
2. Simplify top path
3. Break bootstrap gravity
4. Attachments as first-class module
5. Decouple cache through intents
6. Reminders module
7. Snapshot/rendering split
8. Telegram interaction
9. Access API
10. Final structure and archive
11. Guardrails and done

## Почему именно так

### Сначала канон
Без него рефакторинг снова расползётся.

### Потом верхний путь
Потому что мутный вход разрушает ощущение простоты независимо от остального.

### Потом bootstrap
Потому что пока он центр мира, новые модули будут псевдомодулями.

### Потом attachments
Потому что это лучший первый полигон для real ownership transfer.

### Потом cache decoupling
Потому что это убирает главный аргумент за межмодульную склейку.

### Потом reminders
Потому что там много смешения домена и delivery/runtime.

### Потом snapshot/rendering
Потому что это самый опасный boundary и его нужно резать уже после появления module discipline.

### Потом telegram/access
Потому что к этому моменту уже будет понятный канон, и внешние поверхности лягут на него проще.

### Потом финальная география
Потому что только после реального ownership transfer красота путей отражает правду.

### Потом финальные запреты
Потому что в этот момент уже можно жёстко закрепить новое состояние.

## Запрещённый порядок

Нельзя:
- начинать с массового перемещения файлов;
- начинать с cosmetic docs only;
- одновременно резать все модули;
- оставлять bootstrap до самого конца без ограничений;
- делать guardrails только финальным штрихом.
```

```md
# FILE: work/campaigns/000-architecture-recovery/files-to-read-after-each-step.md

# Что читать после завершения каждой кампании

## После 010
- `docs/architecture-recovery/goals-and-principles.md`
- `docs/architecture-recovery/ownership-and-boundaries.md`
- `docs/architecture/module-boundaries.md`

## После 020
- `docs/architecture-recovery/runtime-canon.md`
- `src/entrypoint/handler.py`
- `src/entrypoint/parse_request.py`

## После 030
- `src/contexts/*/module.py`
- `docs/architecture-recovery/migration-rules.md`

## После 040
- `src/contexts/attachments/public.py`
- `src/contexts/attachments/module.py`
- `docs/architecture/command-ownership.md`

## После 050
- invalidation intents/jobs contracts
- cache/runtime invalidation handling docs
- `docs/architecture/trigger-orchestration.md` if affected

## После 060
- `src/contexts/reminders/public.py`
- `src/contexts/reminders/module.py`
- ownership docs for reminder commands

## После 070
- `src/contexts/snapshot/public.py`
- `src/contexts/rendering/public.py`
- boundary tests between snapshot and rendering

## После 080
- `src/contexts/telegram_interaction/public.py`
- ownership entry for `group_query_reply`

## После 090
- `src/contexts/access_api/public.py`
- route ownership docs

## После 100
- `README.md`
- new active code map
- archive/deprecated paths list

## После 110
- final review checklist
- README
- module boundaries
- command ownership
- route ownership
```

```md
# FILE: work/campaigns/000-architecture-recovery/success-criteria.md

# Критерии успеха всей программы

## Успех считается достигнутым, если одновременно выполнены все пункты

### 1. Вход
- вход занимает 1–2 экрана
- mode routing явный
- нет магического dispatch path
- путь чтения системы виден глазами

### 2. Runtime
- `platform.runtime` не владеет доменной логикой
- queue dispatch ownership-based
- triggers orchestration-only

### 3. Bootstrap
- перестал быть скрытым мозгом проекта
- новые доменные сборки там не живут
- module-local builders стали нормой

### 4. Modules
- все 6 основных модулей существуют как first-class contexts
- public facade каждого модуля очевиден
- ownership сценариев закреплён

### 5. Boundaries
- modules общаются через contracts/public/intents
- rendering не знает snapshot internals
- cache cross-calls заменены intents/jobs
- old implementation clusters больше не нужны для понимания сценария

### 6. Структура
- active code map соответствует docs
- старые competing roots разжалованы или архивированы
- корень проекта не выглядит многоголовым

### 7. Читаемость
- сценарий можно понять за 30–60 секунд по ключевым файлам
- исчезло ощущение “функция вернула функцию, та вызвала ещё функцию”
- новые разработчики читают код сверху вниз, а не через раскопки

## Признаки провала даже при видимом прогрессе

Программа НЕ считается успешной, если:
- модульность выросла “формально”, но путь чтения остался мутным;
- появились новые фасады, но старые пути остались равноправными;
- bootstrap всё ещё знает слишком много;
- ownership сценариев приходится угадывать;
- technical clusters всё ещё воспринимаются как реальные центры системы.
```

```md
# FILE: work/campaigns/000-architecture-recovery/notes-for-maintainers.md

# Напоминания сопровождающим после завершения программы

## 1. Не возвращайтесь к мышлению “куда это воткнуть по слоям”
Правильный вопрос всегда:
> какой owning module владеет этим сценарием?

А не:
- в какой handler это положить;
- в какой services package;
- в какой jobs package;
- в какой helper util.

## 2. Не стройте новый megabootstrap
Если новому сценарию нужен builder, он должен быть в `contexts/<module>/module.py`.

## 3. Не склеивайте модули кэшем
Новые mutating flows должны публиковать aftermath через intents/jobs.

## 4. Не прячьте маршрут за магией
Верхний путь и queue dispatch должны оставаться очевидными.

## 5. Не позволяйте старым кластерам снова стать центром архитектуры
Если historical path по-прежнему существует, он не должен быть:
- нормой;
- местом нового развития;
- обязательным для чтения системы.

## 6. Проверяйте глазами, не только тестами
Архитектура — это не только запреты, но и форма чтения.
Если глазами стало хуже, даже при успешных тестах — вы движетесь не туда.

## 7. Любой спор решайте по главному критерию
Что сильнее делает код:
- module-first,
- ownership-based,
- читаемым сверху вниз.

Если решение улучшает “гибкость”, но ухудшает это — не принимать.
```

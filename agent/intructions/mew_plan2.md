```md
# FILE: work/campaigns/001-module-first-recovery/README.md

# DTM — полная программа перехода к module-first архитектуре

Этот набор файлов задаёт **единый канон архитектурного лечения** проекта DTM.  
Документ предназначен для агента и сопровождающих разработчиков.

Это не “ещё один рефакторинг по слоям”, не “косметическая чистка”, не “обмазывание адаптерами”, не “разложить по красивым папочкам”.

Это программа перехода от состояния:

- ownership сценариев размазан;
- верхний путь выполнения когнитивно мутный;
- новая архитектура существует как надстройка над старой;
- старые implementation-кластеры продолжают жить как реальные центры системы;
- структура `src` визуально читается как смесь исторических зон;

к состоянию:

- система читается сверху вниз;
- вход реально простой;
- `platform.runtime` нейтрален;
- каждый основной сценарий принадлежит конкретному owning module;
- межмодульная координация оформляется через narrow contracts, queue jobs и invalidation intents;
- структура папок эстетична и отражает ownership, а не свалку технических слоёв.

## Главная цель

Сделать DTM **модульным монолитом с жёстким ownership** и понятным сценарным устройством, где:

- верхний вход короткий и очевидный;
- `platform.runtime` владеет только runtime concerns;
- активный код организован вокруг модулей первого класса;
- основной пользовательский read-side — это **основной запрос списка задач**, уже содержащий данные для карточки и attachments;
- attachment publication понимается как **видимость attachment в основном read-model ответа списка задач**;
- старые technical clusters разжалованы или архивированы;
- Telegram bot/webhook interaction удерживается как **reserve capability на минималках**, а не как активный приоритет архитектуры;
- reminders остаются живым и важным сценарием;
- агент не может снова “улучшить архитектуру”, просто наплодив интерфейсов, адаптеров и фасадов без реального переноса ownership.

## Модули первого класса

Активные owning modules:

- `snapshot`
- `rendering`
- `reminders`
- `attachments`
- `access_api`

Отдельный runtime/platform слой:

- `platform.runtime`

Резервный, изолированный, low-maintenance модуль:

- `telegram_interaction`

## Что сейчас считать главным read-сценарием

Главный пользовательский read-сценарий не “открыть карточку и догрузить её отдельным запросом”.

Главный read-сценарий теперь такой:

> Пользователь открывает интерфейс и получает основной read-model запрос списка задач, в котором уже содержатся данные карточки и список attachments.

Это критически важное уточнение.
Все архитектурные решения должны строиться с учётом этого.

## Что сейчас считать важным attachment-сценарием

Ключевой attachment-сценарий:

1. админ загружает attachment;
2. API принимает mutation быстро;
3. attachment проходит async pipeline;
4. preview / conversion / finalize завершаются;
5. основной read-model списка задач помечается stale;
6. read-model / cache обновляется;
7. в следующем основном запросе attachment уже виден пользователю.

Это означает:
- attachment publication point — не upload accepted;
- и не preview done сам по себе;
- а **видимость attachment в основном task-list read-model**.

## Что делать с Telegram

Telegram interaction не является активным приоритетом архитектурной полировки.

Текущая ситуация:
- полноценный бот сейчас не является продуктовым центром;
- Telegram Mini App версия сайта уже существует;
- от Telegram сейчас реально нужен в основном delivery channel для утренних reminders;
- interaction/webhook/bot flow нужен как возможная резервная capability на будущее.

Следовательно:

- не выкидывать Telegram код;
- не тратить disproportionate effort на его “идеальную архитектуру” сейчас;
- изолировать, удерживать на минималках, не давать ему портить новый канон;
- reminders не должны зависеть от полной реорганизации Telegram interaction.

## Самый важный архитектурный запрет

Запрещено подменять сценарную архитектуру технической архитектурой.

Агент **не имеет права** считать архитектурным прогрессом:
- новый adapter;
- новый connector interface;
- новый service wrapper;
- новый facade;
- новый dispatcher layer;

если при этом:

1. ownership сценария не изменился;
2. старый путь не умер;
3. путь чтения не стал короче;
4. структура проекта не стала визуально яснее;
5. read/write/publication модель сценария не стала явной.

## Как пользоваться этим набором

Порядок чтения:

1. `docs/module-first-recovery/goals-and-principles.md`
2. `docs/module-first-recovery/current-scenarios.md`
3. `docs/module-first-recovery/target-system-map.md`
4. `docs/module-first-recovery/publication-model.md`
5. `docs/module-first-recovery/ownership-and-boundaries.md`
6. `docs/module-first-recovery/anti-fake-modularity-rules.md`
7. `docs/module-first-recovery/target-folder-structure.md`
8. `docs/module-first-recovery/runtime-canon.md`
9. `docs/module-first-recovery/migration-rules.md`

Порядок выполнения кампаний:

1. `010-freeze-the-canon.md`
2. `020-top-path-and-runtime-clarity.md`
3. `030-break-bootstrap-gravity.md`
4. `040-attachments-as-real-module.md`
5. `050-publication-and-cache-aftermath.md`
6. `060-reminders-as-real-module.md`
7. `070-snapshot-rendering-hard-boundary.md`
8. `080-access-api-around-primary-read-model.md`
9. `090-telegram-freeze-and-isolate.md`
10. `100-physical-structure-cleanup.md`
11. `110-guardrails-and-done.md`

## Главный критерий успеха

Работа успешна только если в конце:

- по коду можно быстро прыгать глазами;
- путь сценария укладывается примерно в 3–4 перехода;
- `src` выглядит как система, а не как свалка слоёв;
- новый разработчик видит ownership, а не раскопки;
- старые пути перестали быть равноправными;
- модули читаются как небольшие отдельные системы;
- cache invalidation больше не является аргументом за межмодульную склейку.
```

```md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/goals-and-principles.md

# Цели и принципы module-first лечения

## 1. Что лечим

Мы не лечим “недостаток интерфейсов”.
Мы не лечим “нехватку адаптеров”.
Мы не лечим “неидеальную папочную структуру” отдельно от смысла.

Мы лечим состояние, где:

- каноническая единица организации кода всё ещё не модуль;
- ownership сценариев скрыт за transport/runtime/history слоями;
- новый фасад часто просто перенаправляет в старый implementation-cluster;
- верхний путь выполнения формально тонкий, но когнитивно мутный;
- структура `src` конкурирует сама с собой и не даёт красивой визуальной карты.

## 2. Цель

Перевести проект в состояние, где:

- архитектурной единицей становится **сценарно обоснованный owning module**;
- код читается через:
  - `entrypoint`
  - `platform.runtime`
  - `contexts/*`
- старые clusters (`jobs`, `services`, `engines`, `notify`, `telegram` и т.п.) перестают быть архитектурно значимыми;
- read-side, write-side и publication aftermath описаны явно;
- прямое cross-module cache knowledge исчезает.

## 3. Главные принципы

### 3.1. Архитектура строится от сценариев
Любая архитектурная граница должна обосновываться:
- пользовательским сценарием;
- операционным сценарием;
- publication point;
- read/write split.

А не:
- названием SDK;
- коннектором;
- библиотекой;
- удобством добавить ещё один adapter.

### 3.2. Module first
Любой новый сценарий сначала отвечает на вопрос:
> какой owning module им владеет?

И только потом:
- где лежит код;
- какие adapters нужны;
- как устроен routing.

### 3.3. Runtime is neutral
`platform.runtime` владеет только:
- mode classification;
- queue dispatch;
- trigger orchestration;
- health/ops/runtime surfaces;
- publication aftermath processing;
- runtime telemetry/status concerns.

`platform.runtime` не должен владеть:
- attachment lifecycle;
- reminder business logic;
- rendering rules;
- snapshot domain logic;
- access shaping semantics.

### 3.4. One obvious path
Путь сценария должен читаться примерно так:

- entrypoint
- runtime routing
- module public facade
- module use case / domain action

Если для понимания сценария нужны:
- registry;
- factory over factory;
- lazy getter chain;
- adapter around connector around service;
- router -> dispatcher -> shell -> bridge -> handler,

то решение считается когнитивно неудачным.

### 3.5. Old path must die
Новый путь не считается внедрённым, пока старый путь:
- не удалён;
- не разжалован;
- или не переведён в явный deprecated bridge с задачей на удаление.

### 3.6. Cache is aftermath, not glue
Кэш не является доменной связкой между модулями.
После мутации модуль публикует:
- invalidation intent;
- queue job;
- mutation aftermath metadata.

Но модуль не:
- чистит чужой кэш напрямую;
- знает чужие cache internals;
- зовёт чужой internal cache service.

### 3.7. Folder structure must teach the architecture
Структура папок должна визуально обучать правильной модели проекта.
Если `src` выглядит как свалка технических зон, архитектура уже проигрывает независимо от документации.

## 4. Порядок приоритетов

Порядок важности:

1. ownership сценария
2. простота верхнего пути
3. read/write/publication clarity
4. разгрузка bootstrap
5. настоящая модульность, а не фасады поверх старого
6. визуальная чистота структуры
7. архивирование старого мира

## 5. Что не считается успехом

Не считаются успехом:

- новый adapter без смерти старого пути;
- новый facade над старым `jobs/services` кластером;
- новый context, который просто re-export старого engine;
- новая абстракция без сокращения пути чтения;
- новая папка без реального ownership transfer;
- красивые docs без guardrails.

## 6. Критерий качества

Открыв:
- верхний handler;
- public facade модуля;
- module builder;
- use case;

разработчик должен понять сценарий за 30–60 секунд.

Если нет — рефакторинг недостаточен.
```

```md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/current-scenarios.md

# Текущая карта сценариев

Этот документ фиксирует не endpoint-ы и не джобы, а **реальные сценарии**, вокруг которых должна строиться архитектура.

---

## 1. Главные пользовательские сценарии

### 1.1. Пользователь получает основной список задач
#### Актор
Пользователь сайта.

#### Что хочет
Быстро получить основной интерфейс с уже готовыми данными.

#### Что важно
В основном запросе уже содержатся:
- данные для карточки;
- список attachments;
- всё необходимое для UI без отдельного запроса “на карточку”.

#### Архитектурный смысл
Это главный **primary read model scenario**.

#### Owning module
- `access_api`

---

### 1.2. Пользователь видит attachment внутри основного read-model ответа
#### Актор
Пользователь сайта.

#### Что хочет
В основном ответе списка задач видеть attachment как часть готовых данных.

#### Что важно
Attachment должен быть уже опубликован в read-side.
Он не должен дособираться тяжело inline.

#### Архитектурный смысл
Это **publication-visible read scenario**.

#### Owning modules
- `access_api` — читатель и контракт read-side
- `attachments` — жизненный цикл и publication readiness

---

### 1.3. Админ загружает attachment
#### Актор
Администратор.

#### Что хочет
Быстро прикрепить файл к задаче без долгого ожидания в API.

#### Что происходит
- mutation принимается быстро;
- attachment уходит в async pipeline;
- публикация в основном read-model наступает позже.

#### Архитектурный смысл
Это **write-side mutation scenario**.

#### Owning module
- `attachments`

---

### 1.4. Админ ждёт, когда attachment реально появится в основном read-model
#### Актор
Администратор.

#### Что хочет
Понять, что attachment уже опубликован и будет виден пользователям в основном запросе списка задач.

#### Что происходит
- finalize / preview / conversion завершаются;
- read-model списка задач помечается stale;
- кэш обновляется/инвалидируется;
- attachment начинает стабильно возвращаться в основном read-side.

#### Архитектурный смысл
Это **publication scenario**.

#### Owning modules
- `attachments` — attachment lifecycle
- `platform.runtime` — publication aftermath
- `access_api` — видимый read-side

---

### 1.5. Админ удаляет attachment
#### Актор
Администратор.

#### Что хочет
Удалить attachment и перестать видеть его в основном read-model.

#### Что происходит
- принимается mutation;
- attachment удаляется/деактивируется;
- основной read-model обновляется;
- attachment исчезает из пользовательского ответа.

#### Архитектурный смысл
Это **write-side + publication aftermath**.

#### Owning module
- `attachments`

---

### 1.6. Пользователь получает быстрый кэшированный основной запрос
#### Актор
Пользователь сайта.

#### Что хочет
Быстрый ответ без тяжёлой пересборки данных.

#### Что важно
Система должна быстро отдавать уже готовое состояние.
Read-side должен быть кэшированным/подготовленным.

#### Архитектурный смысл
Это **fast primary read-side scenario**.

#### Owning modules
- `access_api`
- `platform.runtime` / read-model cache aftermath mechanics

---

## 2. Snapshot / rendering сценарии

### 2.1. Система обновляет snapshot
#### Актор
Trigger / runtime orchestration.

#### Что хочет
Пересчитать подготовленное состояние из источников.

#### Owning module
- `snapshot`

---

### 2.2. Система нормализует данные
#### Owning module
- `snapshot`

---

### 2.3. Система сохраняет prepared snapshot
#### Owning module
- `snapshot`

---

### 2.4. Система строит представления
#### Сюда входят
- timeline
- представление по дизайнерам
- и другие render/projection outputs

#### Owning module
- `rendering`

#### Boundary
`rendering` не должен знать internal snapshot engine details.

---

## 3. Reminder-сценарии

### 3.1. Trigger morning run
#### Актор
Runtime.

#### Owning module
- `platform.runtime`

#### Важно
Это orchestration, а не reminder domain.

---

### 3.2. Система отбирает задачи для reminders
#### Owning module
- `reminders`

---

### 3.3. Система строит reminder payload
#### Owning module
- `reminders`

---

### 3.4. Система стилизует reminder text
#### Owning module
- `reminders`

---

### 3.5. Система доставляет reminders
#### Owning module
- `reminders`

---

## 4. Runtime / ops сценарии

### 4.1. Система обрабатывает queue commands
#### Owning module
- `platform.runtime`

---

### 4.2. Система оркестрирует timer flow
#### Owning module
- `platform.runtime`

---

### 4.3. Система выполняет publication aftermath
#### Сюда входят
- invalidation
- refresh signals
- republish aftermath handling

#### Owning module
- `platform.runtime`

---

### 4.4. Оператор смотрит health / queue / status
#### Owning module
- `platform.runtime`

---

## 5. Telegram reserve scenarios

### 5.1. Telegram webhook / bot interaction
#### Статус
Не активный продуктовый приоритет.

#### Решение
Поддерживать как reserve capability на минималках.

#### Owning module
- `telegram_interaction`

#### Важно
Не тратить чрезмерные силы на полировку.
Не давать модулю портить active architectural map.

---

## 6. Самые важные сценарии первого приоритета

1. Пользователь получает основной read-model списка задач.
2. В основном read-model уже есть данные для карточки и attachments.
3. Админ загружает attachment.
4. Attachment проходит async pipeline.
5. Attachment публикуется в основном read-model.
6. Система быстро отдаёт кэшированный основной read-side.
7. Система обновляет snapshot.
8. Система строит rendering projections.
9. Система отправляет reminders.
10. Runtime обрабатывает queue commands.
11. Runtime доводит publication aftermath до согласованного состояния.

---

## 7. Как использовать этот документ

Этот документ читать:
- перед проектированием ownership;
- перед разрезанием модулей;
- перед реорганизацией папок;
- перед любым предложением “адаптеров к коннекторам”.

Если proposed solution не улучшает хотя бы один из этих сценариев — оно не считается архитектурным прогрессом.
```

```md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/publication-model.md

# Publication model

## 1. Зачем нужен этот документ

Система не должна мыслиться только через:
- mutation accepted;
- queue job done;
- converter finished.

Для ключевых сценариев нужно фиксировать:

- write accepted point
- processing point
- publication point
- read-side visibility point

Особенно это важно для attachments.

## 2. Основная publication модель для attachments

### 2.1. Write accepted
Админ инициирует upload / attach mutation.
API быстро принимает запрос.

Это **не** означает, что attachment уже виден пользователю.

### 2.2. Processing
Система делает:
- finalize
- metadata bind
- preview / conversion
- auxiliary async steps

Это **не** финальная пользовательская готовность.

### 2.3. Publication aftermath
После завершения attachment lifecycle модуль публикует aftermath:
- invalidation intent
- queue job
- stale marker
- read-model republish trigger

### 2.4. Publication point
Attachment считается опубликованным, когда:
- основной read-model списка задач начинает стабильно возвращать attachment в составе task payload.

Это и есть настоящий publication point.

## 3. Read model definition

### Primary read model
Главный пользовательский read-side сейчас — это **основной запрос списка задач**.

Он уже содержит:
- данные карточки;
- attachments;
- остальные нужные данные интерфейса.

Это главный внешний read contract системы.

## 4. Implications for ownership

### `attachments`
Владеет:
- mutation lifecycle
- preview/conversion readiness
- publication intent emission

### `access_api`
Владеет:
- внешним read contract
- быстрым возвратом already-published state

### `platform.runtime`
Владеет:
- publication aftermath processing
- invalidation handling
- queue-driven read-side refresh mechanics

## 5. Что запрещено

Запрещено:
- считать upload accepted эквивалентом publication complete;
- напрямую чистить чужой read-side cache из attachments;
- смешивать mutation lifecycle и access response shaping;
- прятать publication semantics внутри случайных helpers.

## 6. Как использовать

Этот документ обязателен к прочтению:
- перед кампанией по attachments;
- перед кампанией по access_api;
- перед любой переработкой cache invalidation;
- перед проектированием queue aftermath logic.

Если proposed implementation не фиксирует publication point, решение считается неполным.
```

```md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/ownership-and-boundaries.md

# Ownership и границы модулей

## 1. Главное правило

Каждый значимый сценарий обязан иметь **одного owning module**.

Нельзя оставлять сценарий:
- между runtime и jobs;
- между access handlers и services;
- между attachments и cache helper’ами;
- между reminders и Telegram;
- между snapshot engine и rendering.

## 2. Ownership верхнего уровня

### `platform.runtime`
Владеет:
- mode classification
- queue transport / dispatch
- trigger orchestration
- health/status/ops/runtime surfaces
- publication aftermath handling
- invalidation execution layer

### `attachments`
Владеет:
- request upload
- finalize upload
- attach metadata
- preview / conversion lifecycle
- delete attachment
- cleanup stale attachments
- publication intent emission

### `reminders`
Владеет:
- selection rules
- payload building
- styling
- delivery use case
- reminder-local retries/fallback/accounting if business-significant

### `snapshot`
Владеет:
- ingestion
- normalization
- snapshot update
- snapshot queries through exported contracts

### `rendering`
Владеет:
- render timeline
- render designers
- output/projection generation

### `access_api`
Владеет:
- primary read model contract
- masked/open shaping
- task-list API payload
- browser-safe response assembly

### `telegram_interaction`
Статус:
- reserve module
- isolate and preserve
- no major polish unless product need appears

Владеет:
- reserve bot/webhook interaction paths
- `group_query_reply` if still present as capability

## 3. Жёсткие boundary rules

### Разрешено
Между модулями разрешены только:
- `contexts.other.public`
- `contexts.other.contracts`
- queue command contracts
- invalidation intents
- narrow query contracts

### Запрещено
Запрещены:
- direct import of other module `application`
- direct import of other module `domain`
- direct import of other module `adapters`
- engine leakage
- service leakage
- direct cross-module cache calls

## 4. Особый boundary: snapshot -> rendering

`rendering` может зависеть только от:
- `snapshot.public`
- `snapshot.contracts`

`rendering` не может зависеть от:
- `snapshot_engine` internals
- snapshot repos
- normalization internals
- ingestion details

Это один из самых жёстких запретов всей программы.

## 5. Особый boundary: attachments -> access_api

`attachments` не должен знать:
- access response shaping
- task-list payload assembly
- browser cache details
- чужую read-side схему

`access_api` не должен знать:
- attachment state machine internals
- preview generation internals
- storage implementation details

Связь допускается только через:
- read contracts
- publication aftermath
- invalidation intents/jobs

## 6. Особый boundary: reminders -> telegram
Reminders не должен зависеть от полноценного Telegram interaction module как от центра мира.

Допустимо:
- delivery adapter
- reserve channel integration

Недопустимо:
- reminder business flow размазан по Telegram bot/webhook module

## 7. Особое ownership-решение

### `group_query_reply`
Если capability остаётся в системе, ownership закрепить за `telegram_interaction`.

Не оставлять её сиротой.

## 8. Признак плохой границы

Граница плохая, если:
- без чтения внутренностей другого модуля сценарий непонятен;
- приходится прокидывать engine наружу;
- runtime знает domain-specific assembly слишком глубоко;
- publication осуществляется через скрытый helper;
- модуль “почистил кэш другого модуля руками”.
```

```md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/anti-fake-modularity-rules.md

# Anti-fake-modularity rules

Этот документ нужен, чтобы агент не смог снова подменить реальную модульность декоративной.

## 1. Запрещённая подмена

Не считать архитектурным прогрессом:
- новый adapter;
- новый interface;
- новый service wrapper;
- новый connector abstraction;
- новый facade;
- новый dispatcher;

если при этом:
- ownership сценария не изменился;
- старый путь не умер;
- путь чтения не стал короче;
- структура не стала яснее;
- publication model не стала явной.

## 2. Четыре обязательных вопроса к любому новому слою

Если агент предлагает новый слой, он обязан ответить:

1. какому сценарию принадлежит этот слой?
2. какой owning module им владеет?
3. какой старый путь после этого исчезает?
4. можно ли теперь пройти сценарий глазами быстрее?

Если хотя бы на 2 вопроса ответа нет — изменение запрещено.

## 3. Новый слой должен убить старый
Нельзя:
- добавить новый facade
- оставить старый job/service path
- и заявить, что архитектура улучшилась

Обязательное правило:
- новый слой либо убивает старый;
- либо переводит его в deprecated bridge с явной задачей на удаление;
- иначе изменение считается архитектурным шумом.

## 4. Ограничение на длину path
Сценарий должен прослеживаться максимум примерно за 3–4 перехода:

- entrypoint
- public facade
- use case
- domain/adapters

Если нужно больше — решение подозрительное.

## 5. Запрет на технические top-level центры
В активном каноне `src` запрещено создавать top-level директории как центры системы типа:

- `jobs`
- `services`
- `helpers`
- `engines`
- `routers`
- `handlers`
- `adapters`

как самостоятельные active canonical areas.

Если такой код существует исторически, он должен:
- либо быть внутренностью конкретного модуля;
- либо уйти в archive/deprecated path.

## 6. Запрет на абстракцию ради cold-start эстетики
Lazy-init, getters, factories и wrapper-цепочки допустимы только если:
- они реально нужны;
- не ухудшают path readability;
- не скрывают ownership.

Если ownership стал менее очевиден — архитектурно это ухудшение.

## 7. Папочная эстетика обязательна
Структура папок — не декоративная часть.
Если проект визуально читается как свалка, значит архитектура не завершена.

Любое решение, которое:
- сохраняет хаос верхнего уровня `src`,
- добавляет ещё одну конкурирующую зону,
- или делает структуру менее симметричной,

считается плохим архитектурным решением, даже если локально удобно.

## 8. Как использовать
Читать:
- перед любым предложением нового слоя;
- перед любым рефакторингом через adapter/interface/service;
- перед review результатов кампании.

Если решение выглядит “слишком умным”, сначала проверять его по этому документу.
```

````md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/target-folder-structure.md

# Целевая структура папок

## 1. Зачем отдельный документ

Структура папок должна:
- визуально обучать архитектуре;
- помогать читать код;
- не давать агенту снова свалить всё в корень `src`;
- не поддерживать существование конкурирующих архитектурных центров.

## 2. Целевой верхний вид `src`

```text
src/
  entrypoint/
  platform/
    runtime/
    config/
    infra/
  contexts/
    attachments/
    reminders/
    snapshot/
    rendering/
    access_api/
    telegram_interaction/
  shared/
````

## 3. Что должно быть видно сразу

Открыв `src`, разработчик должен увидеть:

* вход
* runtime/platform
* модули
* shared primitives

И не должен видеть картину:

* тут jobs
* тут services
* тут engines
* тут worker
* тут notify
* тут helpers
* тут adapters
* тут routers

как конкурирующие active centers.

## 4. Целевая симметрия контекстов

Каждый context должен иметь одинаковую и эстетичную форму:

```text
contexts/<module>/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
  docs/
```

### Значение подпапок

* `public.py` — единственный публичный вход модуля
* `module.py` — локальная сборка зависимостей
* `contracts/` — DTO, commands, queries, results, intents
* `application/` — use cases / orchestrators / handlers внутри модуля
* `domain/` — правила, сущности, модели
* `adapters/` — инфраструктурные детали
* `docs/` — модульная документация и migration notes при необходимости

## 5. Жёсткие запреты по структуре

Запрещено создавать новые active top-level directories в `src`, кроме:

* `entrypoint`
* `platform`
* `contexts`
* `shared`

Любое исключение требует очень сильного обоснования и по умолчанию запрещено.

## 6. Что делать со старыми зонами

Старые зоны типа:

* `jobs`
* `services`
* `snapshot_engine`
* `notify`
* `worker`
* `entrypoints_adapters`
* `telegram`
* `render`
* `helpers`

не должны оставаться active canonical map.

Для них допустимы только 4 судьбы:

1. стать внутренностями конкретного модуля;
2. стать runtime/platform internal code;
3. быть явно deprecated;
4. уйти в `archive/`.

## 7. Что считать красивой структурой

Красивая структура — не “много папок”.
Красивая структура — это когда:

* симметрия контекстов очевидна;
* по дереву видно ownership;
* нет конкурирующих центров;
* новый разработчик не задаёт вопрос “где тут вообще настоящая система?”.

## 8. Когда читать

Читать:

* перед любым перемещением файлов;
* перед созданием новой папки в `src`;
* перед финальной cleanup-кампанией.

````

```md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/runtime-canon.md

# Канон runtime и верхнего пути выполнения

## 1. Цель

Верхний путь выполнения должен быть:
- коротким;
- наглядным;
- дешёвым;
- ownership-readable.

## 2. Целевой верхний path

### Нормальный handler
- принимает event
- делает `parse_request`
- делает явный `match/case` по mode
- делегирует в runtime или module public facade

### Нормальный queue path
- runtime parse envelope
- runtime decode command
- runtime dispatch by ownership
- module public facade
- module use case

### Нормальный trigger path
- runtime получает trigger
- runtime emits orchestration plan
- runtime enqueue-ит module-owned commands

## 3. Что должно быть видно глазами
В одном верхнем месте должно быть видно:
- какие mode существуют
- какие runtime paths есть
- какие module paths есть
- какие surfaces platform-owned

## 4. Что запрещено
Запрещены:
- registry magic
- dispatch, который скрывает маршрут
- functions returning functions на основном пути
- deep lazy getter chains
- top-level path, который нельзя понять за 1 экран

## 5. Что разрешено
Разрешены:
- lazy imports внутри явных веток
- минимум wrappers, если они не скрывают ownership
- runtime-only telemetry wrappers
- queue/trigger helpers как runtime detail

## 6. Что нельзя тащить в runtime
Нельзя тащить в runtime:
- attachment state machine
- reminder selection logic
- rendering domain logic
- snapshot normalization rules
- access shaping semantics

## 7. Когда читать
Читать:
- перед кампанией про верхний путь;
- перед review handler/runtime changes;
- если снова появляется ощущение “функция вернула функцию, и стало трудно читать”.
````

```md
# FILE: work/campaigns/001-module-first-recovery/docs/module-first-recovery/migration-rules.md

# Правила миграции

## 1. Сначала ownership, потом география

Нельзя начинать с массового move-only рефакторинга.

Правильный порядок:
1. ownership
2. public facade
3. local module builder
4. path simplification
5. guardrail
6. death of old path
7. physical move / archive

## 2. Один живой модуль за раз

Не надо пытаться одновременно идеально переписать всё.

Приоритет активных модулей:
1. attachments
2. reminders
3. snapshot/rendering boundary
4. access_api

Telegram — отдельно, как low-maintenance isolate.

## 3. Любой новый код живёт только по новому канону
Нельзя добавлять новый сценарий:
- напрямую в старые jobs/services clusters;
- через старый bootstrap;
- без owning module;
- без ясного publication aftermath, если это mutation.

## 4. Deprecated bridges допустимы только как переход
Если старый путь временно нужен:
- он должен быть коротким;
- он должен быть помечен;
- у него должна быть задача на удаление;
- он не должен быть нормой для нового кода.

## 5. После каждой кампании обязателен один убитый старый путь
Если ни один старый путь не умер или хотя бы не разжалован, кампания слишком слабая.

## 6. Обязательная документация после каждой кампании
Обновлять:
- ownership docs
- command ownership
- route ownership
- publication model if affected
- deprecated paths list

## 7. Когда читать
Читать:
- перед началом любой кампании;
- если возникает соблазн “сначала просто красиво переложить папки”.
```

```md
# FILE: work/campaigns/001-module-first-recovery/010-freeze-the-canon.md

# Кампания 010 — зафиксировать канон, сценарии и ранние запреты

## Цель

Остановить дальнейшее расползание архитектуры и зафиксировать:
- сценарный канон;
- ownership-карту;
- publication model;
- anti-fake-modularity запреты;
- целевую структуру папок.

Без этого любая следующая работа снова выродится в полумеры.

## Что сделать

### 1. Создать и заполнить базовые recovery docs
Обязательные файлы:
- `docs/module-first-recovery/goals-and-principles.md`
- `docs/module-first-recovery/current-scenarios.md`
- `docs/module-first-recovery/publication-model.md`
- `docs/module-first-recovery/ownership-and-boundaries.md`
- `docs/module-first-recovery/anti-fake-modularity-rules.md`
- `docs/module-first-recovery/target-folder-structure.md`
- `docs/module-first-recovery/runtime-canon.md`
- `docs/module-first-recovery/migration-rules.md`

### 2. Обновить основные архитектурные документы проекта
Обновить или создать:
- `docs/architecture/module-boundaries.md`
- `docs/architecture/command-ownership.md`
- `docs/architecture/route-ownership.md`
- `docs/architecture/trigger-orchestration.md`

### 3. Зафиксировать ownership-решения
Явно записать:
- primary read model — основной запрос списка задач
- publication point attachments — видимость в этом read model
- Telegram interaction — reserve capability
- `group_query_reply` принадлежит `telegram_interaction`
- cache invalidation не является cross-module domain glue
- `rendering` не имеет права лезть во внутренности snapshot

### 4. Ввести ранние guardrails
Минимальный набор:
- no deep imports into other module internals
- no new `os.getenv` outside config layer
- no new active imports from legacy/archive into active path
- no new direct cross-module cache calls
- no new top-level active directories in `src`

## Что не делать
- не переносить массово код;
- не переписывать полпроекта сразу;
- не делать новую волну фасадов без запретов.

## Definition of Done
Кампания завершена, если:
- документы созданы и согласованы;
- ownership decisions записаны;
- сценарная модель зафиксирована;
- минимум базовые guardrails работают;
- новые изменения уже нельзя вносить “по старому стилю” бесконтрольно.

## После завершения читать
- `020-top-path-and-runtime-clarity.md`
- `docs/module-first-recovery/current-scenarios.md`
- `docs/module-first-recovery/runtime-canon.md`
```

```md
# FILE: work/campaigns/001-module-first-recovery/020-top-path-and-runtime-clarity.md

# Кампания 020 — сделать верхний путь реально понятным

## Цель

Упростить верх системы так, чтобы:
- его можно было понять глазами;
- там не было ощущения “одна функция возвращает другую”;
- путь сценария начинался прозрачно.

## Что сделать

### 1. Нормализовать entrypoint
Довести до канона:
- `src/entrypoint/handler.py`
- `src/entrypoint/parse_request.py`
- `src/entrypoint/modes.py`
- `src/entrypoint/responses.py`

### 2. Сделать верхний routing явным
Верхний `handler` должен:
- вызвать parse_request
- сделать явный `match/case`
- делегировать либо в `platform.runtime`, либо в module public facade

### 3. Развести runtime surfaces и module surfaces
Сделать очевидным на верхнем уровне:
- что platform-owned
- что module-owned

### 4. Уменьшить число верхних делегаторов
Сократить:
- лишние lazy getter chains
- dispatch abstractions, скрывающие маршрут
- wrapper levels, не дающие архитектурной пользы

### 5. Нормализовать platform-owned paths
Явно оформить:
- queue worker entry
- trigger entry
- health/status/info ops surfaces

## Технические задачи
1. Свести mode parsing в один дешёвый step.
2. Причесать top-level handler до 1 экрана.
3. Переписать queue/trigger/http верхнее ветвление в явный readable path.
4. Сократить число промежуточных hops.
5. Обновить tests на top-level routing.

## Запреты
- не строить global app context в handler
- не прятать routing в registry magic
- не плодить новые top-level shell layers без смерти старых

## Definition of Done
Кампания завершена, если:
- верхний handler читается за один экран;
- mode map виден глазами;
- верхний путь стал короче;
- число лишних wrapper-уровней уменьшилось;
- тесты на top routing обновлены.

## После завершения читать
- `030-break-bootstrap-gravity.md`
- `docs/module-first-recovery/runtime-canon.md`
```

```md
# FILE: work/campaigns/001-module-first-recovery/030-break-bootstrap-gravity.md

# Кампания 030 — забрать domain ownership у bootstrap

## Цель

Глобальный bootstrap не должен оставаться скрытым мозгом проекта.

Пока bootstrap знает слишком много о:
- доменных jobs;
- builders сценариев;
- внутренностях модулей;
- wiring всего мира;

новая модульность остаётся декоративной.

## Что сделать

### 1. Зафиксировать module-local build pattern
Каждый active context обязан иметь:
- `public.py`
- `module.py`
- local builder
- local config slice
- local assembly of application/domain/adapters

### 2. Ограничить global bootstrap
Global bootstrap может владеть только:
- shared runtime infra
- config top-level loader entry
- queue/telemetry/runtime primitives

Он не должен вручную собирать доменную внутренность модулей.

### 3. Вытащить domain-specific assembly
Перестать собирать в bootstrap:
- attachments mutation internals
- reminders internals
- rendering internals
- snapshot domain internals
- access_api business assembly

### 4. Controlled transition
Пока bootstrap не исчез полностью:
- он может делегировать в module builders;
- он не должен получать новый domain ownership;
- все новые изменения обязаны идти через module-local builders.

## Технические задачи
1. Создать `module.py` во всех target contexts.
2. Сделать понятный шаблон `get_<module>() / build_<module>()`.
3. Перевести новые и активно меняемые сценарии на local builders.
4. Уменьшить bootstrap knowledge surface.
5. Добавить guardrail: нельзя добавлять новый domain builder в global bootstrap.

## Запреты
- не делать новый красивый megabootstrap
- не смешивать это с массовой физической миграцией файлов
- не оставлять bootstrap как “временный центр мира” без ограничений

## Definition of Done
Кампания завершена, если:
- module builders существуют;
- bootstrap перестал расти domain-specific wiring’ом;
- хотя бы несколько реальных сценариев уже строятся локально;
- есть guardrail против возврата к bootstrap-as-god.

## После завершения читать
- `040-attachments-as-real-module.md`
- `docs/module-first-recovery/ownership-and-boundaries.md`
```

````md
# FILE: work/campaigns/001-module-first-recovery/040-attachments-as-real-module.md

# Кампания 040 — сделать attachments первым настоящим owning module

## Почему это первая большая модульная кампания

`attachments`:
- уже сценарно отчётлив;
- близок к отдельному subsystem;
- имеет понятный lifecycle;
- хорошо показывает difference между fake modularity и real ownership.

## Цель

Сделать `attachments` полноценным owning module для:

- request upload
- finalize upload
- attach metadata
- preview / conversion
- delete
- cleanup
- publication intent emission
- narrow read contracts

## Целевая структура

```text
src/contexts/attachments/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
  docs/
````

## Что сделать

### 1. Выделить public facade

Все attachment сценарии должны входить через:

* `contexts.attachments.public`

### 2. Выделить contracts

Создать:

* commands
* queries
* DTO
* results
* publication aftermath / invalidation intents

### 3. Выделить domain

Создать:

* `attachment_state_machine.py`
* `preview_policy.py`
* `cleanup_policy.py`
* attachment lifecycle models

### 4. Выделить application use cases

Use cases:

* request upload
* finalize upload
* attach metadata
* generate preview
* delete attachment
* cleanup stale
* attachment read contract assembly if needed

### 5. Выделить adapters

Собрать инфраструктурные детали:

* object storage
* signed urls
* preview converter
* attachment repository

### 6. Перевести routes и queue command ownership

Attachment-related routes/commands должны идти только через `attachments.public`.

### 7. Подготовить publication aftermath

Модуль должен:

* не чистить чужой кэш напрямую;
* а публиковать invalidation/publication intent.

## Что запрещено

* оставлять attachment сценарии размазанными по jobs/services/http handlers как норму;
* напрямую знать access_api response shaping;
* напрямую дергать чужой cache invalidation code.

## Обязательные тесты

* attachment lifecycle tests
* finalize/delete/cleanup tests
* preview generation tests
* publication intent emission tests
* routing tests: ownership attachment routes/commands

## Что должно умереть или разжаловаться

После кампании attachment-related code в старых местах должен:

* либо стать thin deprecated bridge;
* либо стать внутренностью `attachments`;
* либо быть помечен к удалению.

## Definition of Done

Кампания завершена, если:

* attachment flow читается как единый module-first контур;
* publication intent стал частью контракта;
* ownership routes/commands переехал в attachments;
* прямые чужие cache calls исчезли или вынесены в следующую кампанию.

## После завершения читать

* `050-publication-and-cache-aftermath.md`
* `docs/module-first-recovery/publication-model.md`

````

```md
# FILE: work/campaigns/001-module-first-recovery/050-publication-and-cache-aftermath.md

# Кампания 050 — вынести publication aftermath и кэш в runtime-owned механизм

## Цель

Убрать главный ложный аргумент за связанность модулей:
- “мы всё равно связаны, потому что надо чистить кэш”.

Кэш и publication aftermath должны стать runtime-owned concern.

## Что сделать

### 1. Ввести invalidation/publication intents
Определить форматы внутренних intents/job payloads.
Например:
- primary read model stale for task(s)
- attachments publication updated
- list projection stale
- access read model refresh needed

### 2. Сделать runtime-owned aftermath handling
Обработчик invalidation/publication aftermath должен жить в:
- `platform.runtime`
- или runtime cache/publication component

но не в business modules.

### 3. Заменить прямые cache calls на intents/jobs
Найти прямые cross-module cache-clearing места и заменить их на:
- invalidation intents
- queue jobs
- aftermath metadata processing

### 4. Зафиксировать publication pipeline
Особенно для attachments:
- mutation accepted
- processing
- publication intent
- read model refresh
- visible in primary read model

## Технические задачи
1. Создать contracts для invalidation/publication intents.
2. Реализовать runtime handling.
3. Перевести attachment aftermath на intents/jobs.
4. Подготовить аналогичный подход для остальных mutation flows по мере необходимости.
5. Добавить tests на:
   - intent emission
   - aftermath handling
   - отсутствие прямых cache cross-calls

## Запреты
- не строить тяжелую event-bus платформу
- не прятать publication semantics в helper-магии
- не оставлять прямые чужие cache manipulations “временно без срока”

## Definition of Done
Кампания завершена, если:
- publication aftermath формализован;
- кэш не является прямым knowledge-link между модулями;
- runtime владеет invalidation handling;
- attachment publication scenario доходит до видимости в primary read model.

## После завершения читать
- `060-reminders-as-real-module.md`
- `080-access-api-around-primary-read-model.md`
````

````md
# FILE: work/campaigns/001-module-first-recovery/060-reminders-as-real-module.md

# Кампания 060 — сделать reminders самостоятельным живым модулем

## Цель

Собрать reminders в отдельный owning module и отделить:
- reminder domain;
- runtime trigger semantics;
- Telegram reserve code;
- delivery internals.

## Что входит в reminders

- selection rules
- reminder payload building
- styling
- delivery use case
- reminder-specific fallback/retry/accounting if needed

## Что не входит в reminders

- trigger `morning` как runtime source
- Telegram bot/webhook interaction as separate reserve capability
- generic queue plumbing
- foreign cache handling

## Целевая структура

```text
src/contexts/reminders/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
  docs/
````

## Что сделать

### 1. Выделить public facade

Reminder commands входят через:

* `contexts.reminders.public.handle_command`

### 2. Выделить domain

Создать:

* selection rules
* reminder models
* reminder policies

### 3. Выделить application

Use cases:

* select reminders
* build payload
* style payload
* send reminders
* fallback / retry / accounting if module-owned

### 4. Выделить adapters

* delivery gateway
* llm styler
* reminder persistence adapter if needed

### 5. Жёстко отделить от runtime и Telegram reserve code

`morning` — это runtime orchestration.
Telegram delivery integration может остаться adapter detail, но не ownership center.

## Что запрещено

* продолжать размазывать reminder logic по notify/jobs/helpers как по нормальным центрам;
* смешивать reminder business rules с Telegram reserve module.

## Обязательные тесты

* selection tests
* payload building tests
* send flow tests
* fallback tests
* ownership routing tests

## Definition of Done

Кампания завершена, если:

* reminder flow читается как отдельный модуль;
* `morning` не воспринимается как часть reminder domain;
* Telegram reserve code не является prerequisite для напоминаний;
* старый notify-centric code разжалован.

## После завершения читать

* `070-snapshot-rendering-hard-boundary.md`
* `090-telegram-freeze-and-isolate.md`

````

```md
# FILE: work/campaigns/001-module-first-recovery/070-snapshot-rendering-hard-boundary.md

# Кампания 070 — ввести жёсткий boundary между snapshot и rendering

## Почему это критично

Если `rendering` продолжает читать внутренности snapshot engine, значит модульность фиктивна.

Это один из самых важных архитектурных швов всего проекта.

## Цель

Получить два реально разных owning modules:

- `snapshot`
- `rendering`

с узким anti-corruption boundary.

## Что сделать

### 1. Нормализовать snapshot
Собрать внутри:
- ingestion
- normalization
- snapshot update
- prepared query contracts
- snapshot repos/adapters

### 2. Нормализовать rendering
Собрать внутри:
- render timeline
- render designers
- projection generation
- render-specific writeback/output logic

### 3. Ввести narrow contracts
`rendering` получает от `snapshot` только:
- public queries
- DTO
- prepared read representations

И ничего больше.

### 4. Убрать прямые internal dependencies
Найти и убрать:
- direct imports
- engine leaks
- internal state reads
- service/helper shortcuts

### 5. Закрепить boundary guardrails
Добавить tests/scripts, запрещающие:
- `rendering` -> snapshot internals

## Технические задачи
1. Довести `contexts/snapshot/public.py` и `module.py`.
2. Довести `contexts/rendering/public.py` и `module.py`.
3. Вынести snapshot contracts.
4. Вынести rendering contracts.
5. Перевести snapshot/render queue commands на правильный ownership.
6. Добавить anti-corruption tests.

## Что запрещено
- оставлять “временный доступ к engine” как норму;
- считать capability-wrapper над engine финальной архитектурой.

## Definition of Done
Кампания завершена, если:
- `snapshot` и `rendering` читаются как разные модули;
- `rendering` больше не зависит от snapshot internals;
- boundary закреплён в tests/docs.

## После завершения читать
- `080-access-api-around-primary-read-model.md`
- `docs/module-first-recovery/ownership-and-boundaries.md`
````

````md
# FILE: work/campaigns/001-module-first-recovery/080-access-api-around-primary-read-model.md

# Кампания 080 — собрать access_api вокруг primary read model

## Цель

Сделать `access_api` настоящим owning module для внешнего read-side контракта, а не просто ярлыком над handlers.

## Главный сценарий
`access_api` должен владеть:
- основным запросом списка задач;
- который уже содержит данные карточки и attachments;
- и быстро отдаваться как primary read model.

## Что должно входить в access_api

- primary read model contract
- masked/open behavior
- response shaping
- browser-safe DTO
- task-list read-side assembly orchestration

## Что не должно входить в access_api

- snapshot ingestion
- rendering internals
- attachments lifecycle internals
- direct cache invalidation mechanics
- runtime queue logic

## Целевая структура

```text
src/contexts/access_api/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
  docs/
````

## Что сделать

### 1. Выделить public facade

Внешний task-list/read-side HTTP path должен входить через:

* `contexts.access_api.public.handle_http_request`

### 2. Выделить domain/application

* access policy
* masked/open shaping
* primary read model response assembly
* response DTO contracts

### 3. Развести ownership с attachments

`access_api` читает attachment publication result через read contracts.
Он не знает attachment internal lifecycle.

### 4. Развести ownership с runtime cache layer

`access_api` не должен владеть чужой invalidation логикой.

## Технические задачи

1. Зафиксировать primary read model contract.
2. Перевести main task-list path в owning module.
3. Вынести shaping/masking/payload assembly.
4. Обновить route ownership docs.
5. Добавить tests:

   * primary response shape
   * masked/open modes
   * attachment visibility through published state

## Запреты

* не строить access_api как thin alias над legacy handlers
* не позволять ему напрямую читать internal module internals

## Definition of Done

Кампания завершена, если:

* access_api стал реальным owning module внешнего read-side;
* основной task-list scenario принадлежит ему явно;
* attachment visibility идёт через publication-ready state, а не internal knowledge.

## После завершения читать

* `090-telegram-freeze-and-isolate.md`
* `100-physical-structure-cleanup.md`

````

```md
# FILE: work/campaigns/001-module-first-recovery/090-telegram-freeze-and-isolate.md

# Кампания 090 — Telegram freeze and isolate

## Цель

Не вылизывать Telegram interaction как активный приоритет, но и не дать ему портить active architecture.

Telegram сейчас — reserve capability:
- не центральный продуктовый сценарий;
- не стоит тратить большие силы на полировку;
- нельзя и выкинуть, потому что может понадобиться позже.

## Что нужно получить

- Telegram code изолирован;
- ownership зафиксирован;
- reserve capability не течёт в active modules;
- reminders не зависят от полного bot/webhook module;
- старый Telegram код не остаётся архитектурным центром.

## Что сделать

### 1. Зафиксировать статус
В документации явно записать:
- `telegram_interaction` = reserve isolated module
- low maintenance
- no deep modernization unless product need appears

### 2. Закрепить ownership
Если остаются:
- webhook paths
- bot interaction paths
- `group_query_reply`

они принадлежат `telegram_interaction`.

### 3. Развести с reminders
Reminder delivery through Telegram channel может жить как adapter detail reminders, но не как reason тянуть весь Telegram module в active priority.

### 4. Изолировать код
Перевести Telegram code в:
- отдельный context/zone
- без расползания по runtime/notify/reminders

### 5. Разжаловать старые Telegram-specific clusters
Если исторические telegram paths ещё живут:
- они должны быть либо внутренностью `telegram_interaction`,
- либо deprecated bridge.

## Что не делать
- не тратить disproportionate effort на polished bot architecture
- не удалять reserve capability
- не смешивать это с active scenario architecture

## Обязательные тесты
Минимально:
- ownership tests for remaining telegram paths
- isolation tests if feasible

## Definition of Done
Кампания завершена, если:
- Telegram code изолирован;
- он больше не портит active architectural map;
- reminders независимы от полного Telegram interaction refactor;
- reserve capability можно поддерживать с минимумом усилий.

## После завершения читать
- `100-physical-structure-cleanup.md`
- `docs/module-first-recovery/target-folder-structure.md`
````

````md
# FILE: work/campaigns/001-module-first-recovery/100-physical-structure-cleanup.md

# Кампания 100 — финальная физическая cleanup структуры

## Цель

Только после ownership transfer и module builders привести физическую структуру в эстетичное состояние.

Цель кампании:
- сделать `src` красивым и обучающим архитектуре;
- убрать competing centers;
- сделать структуру симметричной;
- убрать ощущение свалки.

## Что сделать

### 1. Привести active `src` к целевому виду
Оставить активный канон:

```text
src/
  entrypoint/
  platform/
    runtime/
    config/
    infra/
  contexts/
    attachments/
    reminders/
    snapshot/
    rendering/
    access_api/
    telegram_interaction/
  shared/
````

### 2. Разжаловать старые technical clusters

Старые зоны должны:

* либо стать внутренностями модулей;
* либо стать deprecated;
* либо уйти в archive;
* либо перестать быть active canonical paths.

### 3. Почистить корень проекта

Корень и `src` не должны выглядеть многоголовыми.

### 4. Обновить README и docs navigation

README должен показывать:

* только новый путь чтения
* только новую active code map
* только новый канон

## Технические задачи

1. Переместить surviving active code в правильные зоны.
2. Обновить imports.
3. Обновить docs navigation.
4. Добавить deprecated/archived list.
5. Добавить guardrail: нельзя развивать archived/deprecated paths как active center.

## Запреты

* не делать косметический move-only раньше времени
* не оставлять две равноправные архитектурные карты
* не держать old technical cluster как “ну пока так тоже можно”

## Definition of Done

Кампания завершена, если:

* активная структура соответствует target folder structure;
* `src` выглядит эстетично;
* старые competing roots разжалованы;
* README и docs ведут только в новый канон.

## После завершения читать

* `110-guardrails-and-done.md`
* `docs/module-first-recovery/target-folder-structure.md`

````

```md
# FILE: work/campaigns/001-module-first-recovery/110-guardrails-and-done.md

# Кампания 110 — финальные guardrails и критерии завершения

## Цель

Закрепить новую архитектуру так, чтобы она не расползлась обратно.

## Что сделать

### 1. Добавить architecture guardrails
Обязательные проверки:
- no deep imports into other module internals
- no active imports from archive/legacy
- no `os.getenv` outside config
- no direct cross-module cache calls
- no new top-level active dirs in `src`
- no `rendering` -> snapshot internals
- no growth of global bootstrap domain ownership
- no new fake-modularity layers without killing old path

### 2. Добавить readability guardrails
Нужны checks на:
- handler size / complexity
- public.py thinness
- module.py not becoming new god-file
- runtime files not bloating uncontrollably

### 3. Обновить contribution rules
Зафиксировать:
- как добавлять новый сценарий
- как определять owning module
- как оформлять aftermath intents
- как оформлять deprecated bridges
- что считать forbidden shortcut

### 4. Провести финальную архитектурную ревизию
Проверить:
- primary read model ownership
- attachment publication path
- reminders
- snapshot/rendering boundary
- Telegram reserve isolation
- structure aesthetics

## Финальный Definition of Done

Программа завершена только если одновременно верны все условия:

1. Верхний handler короткий и понятный.
2. `platform.runtime` нейтрален.
3. Bootstrap перестал быть скрытым мозгом системы.
4. Основной task-list response оформлен как primary read model.
5. Attachments публикуются в этот read model через publication aftermath, а не через hidden cache hacks.
6. `attachments`, `reminders`, `snapshot`, `rendering`, `access_api` существуют как реальные first-class contexts.
7. `rendering` не знает snapshot internals.
8. Cache coupling вынесен в intents/jobs/runtime layer.
9. Telegram interaction изолирован и не мешает active architecture.
10. `src` выглядит как эстетичная, ясная карта системы.
11. Старые technical clusters перестали быть архитектурными центрами.
12. По коду можно быстро пройти сценарий глазами без цепочки мутных мостов.

## Финальная ручная проверка

Открыть подряд:
- `src/entrypoint/handler.py`
- `src/entrypoint/parse_request.py`
- `src/platform/runtime/queue_dispatch.py`
- `src/platform/runtime/orchestration.py`
- `src/contexts/attachments/public.py`
- `src/contexts/attachments/module.py`
- `src/contexts/reminders/public.py`
- `src/contexts/snapshot/public.py`
- `src/contexts/rendering/public.py`
- `src/contexts/access_api/public.py`

И ответить:

1. Я вижу ли карту системы без археологии?
2. Ясно ли, кто владеет сценарием?
3. Путь сценария короче и прямее?
4. Старые пути умерли или разжалованы?
5. `src` выглядит красиво и понятно?
6. Нет ли ощущения “функция вернула функцию, а дальше ещё лабиринт”?

Если минимум на 2 вопроса ответ “нет”, программа не завершена.
````

```md
# FILE: work/campaigns/001-module-first-recovery/tasks/attachments-task-list.md

# Task list — attachments

## Основные задачи
- Собрать ownership attachment сценариев в одном модуле
- Выделить contracts / application / domain / adapters
- Выделить attachment state machine
- Выделить preview / cleanup policies
- Ввести publication aftermath intent emission
- Перевести routes и commands на `attachments.public`
- Убрать прямые cross-module cache calls
- Обновить docs and tests

## Нельзя забыть
- publication point = видимость в primary read model
- upload accepted != published
- old paths must die or become deprecated bridges
```

```md
# FILE: work/campaigns/001-module-first-recovery/tasks/reminders-task-list.md

# Task list — reminders

## Основные задачи
- Собрать selection / payload / style / delivery в owning module
- Отделить от runtime trigger semantics
- Отделить от Telegram reserve code
- Выделить local adapters
- Перевести commands ownership
- Разжаловать старые notify-centric paths
- Обновить docs and tests

## Нельзя забыть
- `morning` принадлежит runtime
- reminders — активный живой сценарий первого приоритета
- Telegram interaction — не prerequisite для reminders
```

```md
# FILE: work/campaigns/001-module-first-recovery/tasks/snapshot-rendering-task-list.md

# Task list — snapshot/rendering

## Основные задачи
- Довести snapshot до реального owning module
- Довести rendering до реального owning module
- Ввести narrow contracts
- Убрать internal engine leaks
- Добавить anti-corruption tests
- Перевести queue commands ownership
- Обновить docs

## Нельзя забыть
- rendering не имеет права читать snapshot internals
- capability wrappers над старым engine — это не финальная цель
```

```md
# FILE: work/campaigns/001-module-first-recovery/tasks/access-api-task-list.md

# Task list — access_api

## Основные задачи
- Зафиксировать primary read model contract
- Оформить task-list response как owning scenario access_api
- Выделить shaping / masking / response assembly
- Убрать direct internal reads
- Развести ownership с attachments lifecycle
- Подготовить tests для response shape and attachment visibility
- Обновить docs

## Нельзя забыть
- отдельного card-details request как primary scenario сейчас нет
- primary read model = основной запрос списка задач
```

```md
# FILE: work/campaigns/001-module-first-recovery/tasks/telegram-task-list.md

# Task list — telegram reserve module

## Основные задачи
- Зафиксировать reserve status
- Закрепить ownership remaining paths
- Изолировать код
- Не дать модулю течь в active contexts
- Разжаловать старые Telegram clusters
- Обновить docs

## Нельзя забыть
- не вылизывать лишнего
- не удалять целиком
- reminders не должны зависеть от глубокой полировки Telegram module
```

```md
# FILE: work/campaigns/001-module-first-recovery/checklists/after-each-campaign.md

# Чеклист после каждой кампании

## 1. Ownership
- Стало ли понятнее, какой модуль владеет сценарием?
- Убрали ли ambiguous ownership zone?
- Обновили ли ownership docs?

## 2. Path readability
- Стал ли путь сценария короче?
- Уменьшилось ли число мостов/делегаторов?
- Уменьшилось ли ощущение “функция вернула функцию”?

## 3. Old path death
- Умер ли хотя бы один старый путь?
- Или хотя бы стал deprecated bridge?
- Есть ли срок/задача на удаление переходного пути?

## 4. Read/write/publication clarity
- Стало ли понятнее, где mutation, где publication, где read-side?
- Для affected scenarios publication point зафиксирован?

## 5. Guardrails
- Добавлен ли новый запрет/test?
- Можно ли теперь случайно откатиться назад без fail?

## 6. Folder aesthetics
- Стала ли структура визуально чище?
- Не появился ли новый competing center в `src`?

Если минимум на 4 из 6 пунктов ответ “нет”, кампания не завершена.
```

```md
# FILE: work/campaigns/001-module-first-recovery/checklists/final-review.md

# Финальный ревью-чеклист

## Верхний путь
- handler короткий
- parse_request дешёвый и понятный
- mode map явный
- path читается глазами

## Runtime
- runtime нейтрален
- queue dispatch ownership-based
- trigger orchestration не владеет доменной логикой
- publication aftermath runtime-owned

## Bootstrap
- global bootstrap не центр мира
- новые domain builders не живут там
- module-local builders норма

## Модули
- attachments first-class
- reminders first-class
- snapshot first-class
- rendering first-class
- access_api first-class
- telegram reserve isolated

## Boundaries
- rendering не знает snapshot internals
- attachments не знают access_api shaping internals
- cache coupling вынесен
- межмодульные связи только narrow

## Структура
- `src` эстетичен
- нет competing active centers
- docs совпадают с active map

## Главный вопрос
Можно ли пройти основной сценарий глазами быстро и без раскопок?

Если нет — архитектурное лечение не завершено.
```

```md
# FILE: work/campaigns/001-module-first-recovery/agent-instructions.md

# Инструкции агенту

Работай по этим правилам без самовольной подмены цели.

## 1. Что именно нужно сделать

Нужно не “улучшить код вообще”, а перевести DTM в module-first архитектуру, где:
- активная система читается через `entrypoint`, `platform.runtime`, `contexts/*`;
- основной read-side сценарий — основной запрос списка задач;
- attachments публикуются в этом read model;
- reminders остаются активным важным сценарием;
- Telegram interaction удерживается как reserve isolated module;
- fake modularity запрещена.

## 2. Что считается ошибкой

Ошибкой считается:
- построить новый adapter/interface/service layer без смерти старого пути;
- скрыть path за registry/factory magic;
- улучшить “формальную модульность”, не улучшив читаемость;
- оставить ownership сценария в старом jobs/services cluster;
- развивать старые технические зоны как active architectural centers;
- портить эстетику `src`.

## 3. Что делать обязательно

Обязательно:
- мыслить от сценариев, publication point и read/write split;
- задавать owning module для каждого сценария;
- вводить local module builders;
- убирать domain ownership из bootstrap;
- выносить cache coupling в intents/jobs;
- делать структуру `src` визуально чистой;
- после каждой кампании убивать хотя бы один старый путь.

## 4. Запрет на ложную модульность

Не считай архитектурным прогрессом:
- новый facade
- новый adapter
- новый interface
- новый service wrapper
- новый dispatcher

если ownership сценария остался там же, где был.

## 5. Как принимать решения

Если есть выбор между:
- архитектурно “умнее”, но менее читаемо;
- чуть проще, но явно видно путь сценария;

выбирай второе.

В этом проекте:
- наглядность,
- ownership,
- сценарная ясность,
- и эстетика структуры
важнее абстракции ради абстракции.

## 6. Как оценивать свой шаг

После каждого шага спроси:
1. ownership стал яснее?
2. путь сценария стал короче?
3. старый путь умер или ослаблен?
4. publication/read/write модель стала понятнее?
5. структура стала визуально лучше?

Если нет — шаг слабый.

## 7. Порядок кампаний

Строго идти по порядку:

1. `010-freeze-the-canon.md`
2. `020-top-path-and-runtime-clarity.md`
3. `030-break-bootstrap-gravity.md`
4. `040-attachments-as-real-module.md`
5. `050-publication-and-cache-aftermath.md`
6. `060-reminders-as-real-module.md`
7. `070-snapshot-rendering-hard-boundary.md`
8. `080-access-api-around-primary-read-model.md`
9. `090-telegram-freeze-and-isolate.md`
10. `100-physical-structure-cleanup.md`
11. `110-guardrails-and-done.md`

Не перескакивать без сильного основания.

## 8. Как относиться к Telegram
Telegram interaction:
- не выкидывать;
- не шлифовать до идеала;
- держать как reserve isolated module;
- не позволять ему портить active architecture.

## 9. Как относиться к folder structure
Папки — часть архитектуры.
Нельзя снова делать `src` похожим на свалку технических зон.
Новая top-level active папка вне:
- `entrypoint`
- `platform`
- `contexts`
- `shared`

по умолчанию запрещена.

## 10. Как выглядит успех
Успех — это не “модульность выросла”.
Успех — это когда:
- ownership видно глазами;
- основной сценарий читается быстро;
- старые пути разжалованы;
- `src` красив;
- система выглядит как единое аккуратное произведение, а не как раскопки.
```

```md
# FILE: work/campaigns/001-module-first-recovery/files-to-read-by-situation.md

# Какие файлы читать и в каких случаях

## Если проектируешь ownership нового сценария
Читать:
- `docs/module-first-recovery/current-scenarios.md`
- `docs/module-first-recovery/ownership-and-boundaries.md`
- `docs/architecture/command-ownership.md`
- `docs/architecture/route-ownership.md`

## Если кажется, что нужен новый adapter/interface/service
Читать:
- `docs/module-first-recovery/anti-fake-modularity-rules.md`

## Если меняешь верхний path
Читать:
- `docs/module-first-recovery/runtime-canon.md`
- `020-top-path-and-runtime-clarity.md`

## Если меняешь mutation flow
Читать:
- `docs/module-first-recovery/publication-model.md`
- `050-publication-and-cache-aftermath.md`

## Если меняешь read-side сайта
Читать:
- `docs/module-first-recovery/current-scenarios.md`
- `080-access-api-around-primary-read-model.md`

## Если меняешь attachments
Читать:
- `040-attachments-as-real-module.md`
- `docs/module-first-recovery/publication-model.md`
- `tasks/attachments-task-list.md`

## Если меняешь reminders
Читать:
- `060-reminders-as-real-module.md`
- `tasks/reminders-task-list.md`

## Если меняешь snapshot/rendering
Читать:
- `070-snapshot-rendering-hard-boundary.md`
- `tasks/snapshot-rendering-task-list.md`

## Если думаешь, что Telegram надо трогать
Читать:
- `090-telegram-freeze-and-isolate.md`
- `tasks/telegram-task-list.md`

## Если меняешь структуру папок
Читать:
- `docs/module-first-recovery/target-folder-structure.md`
- `100-physical-structure-cleanup.md`

## Если подводишь итог или принимаешь работу
Читать:
- `checklists/after-each-campaign.md`
- `checklists/final-review.md`
- `110-guardrails-and-done.md`
```

```md
# FILE: work/campaigns/001-module-first-recovery/success-criteria.md

# Критерии успеха всей программы

Успех считается достигнутым только если одновременно верны все пункты:

## 1. Сценарии
- ownership всех основных сценариев ясен
- главный read-side scenario зафиксирован как основной запрос списка задач
- publication point attachments явно определён

## 2. Верхний путь
- handler короткий и понятный
- mode routing явный
- runtime/module split виден глазами

## 3. Runtime
- runtime нейтрален
- queue dispatch ownership-based
- publication aftermath runtime-owned

## 4. Bootstrap
- bootstrap перестал быть скрытым мозгом
- module-local builders стали нормой

## 5. Modules
- attachments real first-class module
- reminders real first-class module
- snapshot real first-class module
- rendering real first-class module
- access_api real first-class module
- telegram reserve isolated

## 6. Boundaries
- rendering не знает snapshot internals
- attachments не знают access_api internals
- cache cross-calls исчезли
- межмодульные связи narrow и явные

## 7. Structure
- `src` выглядит красиво и симметрично
- нет новых competing centers
- старые zones разжалованы или архивированы

## 8. Readability
- сценарий прослеживается примерно за 3–4 перехода
- нет ощущения бесконечной цепочки “функция возвращает функцию”
- код можно показывать как сильную архитектурную работу

## Признаки провала даже при прогрессе
Программа не считается успешной, если:
- modularity выросла формально, но читать код всё ещё мутно;
- contexts остались фасадами поверх старых clusters;
- bootstrap по-прежнему знает слишком много;
- structure cleanup не завершён;
- docs говорят одно, а active code map показывает другое.
```

```md
# FILE: work/campaigns/001-module-first-recovery/notes-for-maintainers.md

# Напоминания сопровождающим после внедрения

## 1. Любой новый сценарий начинается с ownership
Вопрос номер один:
> какой owning module этим владеет?

Не спрашивать сначала:
- в какой handler это положить;
- в какой service;
- в какой job;
- в какой helper.

## 2. Не стройте новый megabootstrap
Если сценарию нужен builder, он должен быть в `contexts/<module>/module.py`.

## 3. Не склеивайте модули кэшем
После мутаций публикуйте intents/jobs.

## 4. Не прячьте маршрут за умной абстракцией
Path важнее абстрактной красоты.

## 5. Держите `src` красивым
Структура верхнего уровня — часть архитектурной дисциплины.

## 6. Telegram не делайте центром мира
Поддерживайте как reserve isolated module, пока не появится реальная продуктовая причина.

## 7. Проверяйте глазами
Если тесты зелёные, но сценарий глазами стал читать тяжелее — вы движетесь не туда.

## 8. Главный критерий
Архитектура должна:
- уменьшать когнитивную нагрузку;
- делать ownership видимым;
- и выглядеть эстетично.
```

```md
# FILE: work/campaigns/001-module-first-recovery/implementation-order.md

# Порядок внедрения

## Обязательный порядок

1. Freeze canon, scenarios, rules
2. Simplify top path
3. Break bootstrap gravity
4. Make attachments a real module
5. Move cache/publication aftermath into runtime
6. Make reminders a real module
7. Enforce snapshot/rendering boundary
8. Build access_api around primary read model
9. Freeze and isolate Telegram reserve module
10. Cleanup physical structure
11. Add final guardrails and accept only if readability improved

## Почему именно так

### Сначала канон
Без канона агент снова уйдёт в декоративные фасады.

### Потом верхний путь
Потому что мутный вход убивает ощущение архитектуры независимо от остального.

### Потом bootstrap
Потому что пока он центр мира, новые contexts не настоящие.

### Потом attachments
Потому что там лучше всего видно publication model и fake modularity.

### Потом publication aftermath
Потому что это главный оставшийся “клей” между модулями.

### Потом reminders
Потому что это активный важный сценарий, который нельзя зависеть от Telegram reserve.

### Потом snapshot/rendering
Потому что это самый опасный boundary.

### Потом access_api
Потому что к этому моменту уже можно правильно оформить primary read model.

### Потом Telegram
Потому что он не должен отнимать внимание раньше активных модулей.

### Потом физическая cleanup
Потому что только после ownership transfer красота путей отражает правду.

### Потом финальные guardrails
Потому что в этот момент уже есть что жёстко закрепить.
```

```md
# FILE: work/campaigns/001-module-first-recovery/main-command-to-agent.md

# Главная команда агенту

Выполни архитектурное лечение DTM как переход к module-first modular monolith. Проектируй не от библиотек, не от SDK, не от коннекторов и не от adapter/interface слоёв, а от реальных пользовательских и системных сценариев. Зафиксируй основной read-side как primary read model — основной запрос списка задач, который уже содержит данные карточки и attachments. Проектируй attachment publication не как “upload accepted”, а как видимость attachment в этом основном read model. Построй активную систему вокруг `entrypoint`, `platform.runtime`, `contexts/attachments`, `contexts/reminders`, `contexts/snapshot`, `contexts/rendering`, `contexts/access_api`, а `telegram_interaction` удерживай как reserve isolated module без лишней полировки. Не создавай новые adapter/facade/interface/service layers, если ownership сценария не меняется и старый путь не умирает. После каждой кампании делай путь сценария короче, ownership яснее, структуру `src` эстетичнее и вводи guardrails, чтобы нельзя было откатиться к старому стилю.
```

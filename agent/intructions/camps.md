````md
# DTM — прикладной набор кампаний на архитектурную переделку

Этот документ — не описание идеала, а **рабочий план внедрения**. Его задача: дать агенту и разработчику понятную последовательность шагов, чтобы переделка шла безопасно, без потери текущих сценариев, без расползания архитектуры и без соблазна снова свалить всё в один жирный runtime.

---

# 0. Общие правила выполнения

Перед началом любой кампании соблюдать следующие правила.

## 0.1. Инварианты, которые нельзя ломать
Нужно сохранить рабочими следующие сценарии:

- HTTP frontend/API сценарии;
- queue worker сценарии;
- `timer` trigger;
- `morning` trigger;
- Telegram webhook intake;
- snapshot update;
- timeline/designers rendering;
- reminders flow;
- attachment workflow:
  - request upload;
  - finalize;
  - metadata attach;
  - preview;
  - delete;
  - cleanup;
  - read/download/view.

## 0.2. Общий стиль изменений
Каждая кампания должна:

- быть атомарной по смыслу;
- не смешивать архитектурный перенос и случайные улучшения;
- сопровождаться обновлением документации;
- сопровождаться тестами или адаптацией существующих тестов;
- не оставлять после себя “временных костылей без задачи на удаление”.

## 0.3. Что запрещено в любой кампании
Запрещено:

- тащить новую бизнес-логику в `entrypoint`;
- делать новый глобальный mega-bootstrap;
- плодить новые top-level active code roots вне `src/`;
- добавлять глубокие cross-module imports;
- прятать routing в магический dispatch registry;
- складывать всё спорное в `shared/`;
- одновременно менять архитектуру и предметную логику без крайней необходимости.

## 0.4. Правило завершения кампании
Кампания считается завершённой только если:

- код проходит тесты;
- документация обновлена;
- временные переходные места либо удалены, либо явно помечены;
- новая структура читается лучше старой;
- изменения не ухудшили прозрачность точки входа.

---

# 1. Порядок кампаний

Работу выполнять строго в таком порядке:

1. Зафиксировать архитектурный договор и карту ownership.
2. Построить новый skeleton `src/entrypoint`, `src/platform`, `src/contexts`.
3. Перевести верхний handler на тонкий mode-routing.
4. Перевести queue worker на явный command-routing.
5. Вынести trigger orchestration.
6. Выделить `attachments`.
7. Выделить `reminders`.
8. Разделить `snapshot` и `rendering`.
9. Выделить `telegram_interaction`.
10. Выделить `access_api`.
11. Централизовать config/runtime setup.
12. Архивировать legacy и зачистить корень.
13. Добавить архитектурные guardrails и финальную полировку.

---

# 2. Кампания A — архитектурный договор и ownership-карта

## Цель
Сначала зафиксировать, что именно считается новой системой, иначе перенос пойдёт хаотично.

## Что сделать
Создать и заполнить документы:

- `docs/overview/system-map.md`
- `docs/architecture/module-boundaries.md`
- `docs/architecture/command-ownership.md`
- `docs/architecture/route-ownership.md`
- `docs/architecture/trigger-orchestration.md`

Создать модульные документы:

- `docs/modules/snapshot.md`
- `docs/modules/rendering.md`
- `docs/modules/reminders.md`
- `docs/modules/telegram_interaction.md`
- `docs/modules/attachments.md`
- `docs/modules/access_api.md`

Обновить `README.md`:
- показать active system map;
- показать, где читать вход;
- показать, что активный код живёт в `src/`.

## Что должно быть внутри документов
### `module-boundaries.md`
Явно описать:
- какие есть контексты;
- какие папки кому принадлежат;
- как модули могут общаться;
- что считается запрещённым импортом.

### `command-ownership.md`
Таблица:
- command type;
- owning module;
- runtime entry;
- expected side effects.

### `route-ownership.md`
Таблица:
- route/path;
- owning module;
- transport type;
- sync/async semantics.

### `trigger-orchestration.md`
Таблица:
- trigger;
- orchestration owner;
- emitted commands;
- expected status/result.

## Результат
Появляется формальный архитектурный договор, от которого дальше нельзя отступать.

---

# 3. Кампания B — построить новый skeleton проекта

## Цель
Подготовить конечную структуру до массового переноса логики.

## Что создать
Создать каталоги:

```text
src/
  entrypoint/
  platform/
    runtime/
    config/
    infra/
    shell/
  shared/
  contexts/
    snapshot/
    rendering/
    reminders/
    telegram_interaction/
    attachments/
    access_api/
````

В каждом контексте создать минимум:

```text
public.py
module.py
contracts/
application/
domain/
adapters/
```

Создать файлы:

```text
src/entrypoint/handler.py
src/entrypoint/parse_request.py
src/entrypoint/modes.py
src/entrypoint/responses.py

src/platform/runtime/classify.py
src/platform/runtime/queue_dispatch.py
src/platform/runtime/orchestration.py
```

## Что пока не делать

Пока не переносить всю бизнес-логику.
Сначала только каркас и пустые фасады.

## Технические задачи

* в `public.py` каждого контекста сделать минимальный публичный вход;
* в `module.py` каждого контекста сделать пустой/временный builder;
* добавить комментарии-шаблоны в файлы, чтобы не было соблазна нарушить назначение.

## Результат

Архитектурный каркас появляется в коде раньше, чем туда потечёт реальная логика.

---

# 4. Кампания C — тонкий entrypoint и mode routing

## Цель

Сделать один очень ясный вход в систему.

## Что сделать

Реализовать:

* `src/entrypoint/modes.py`
* `src/entrypoint/parse_request.py`
* `src/entrypoint/handler.py`
* `src/entrypoint/responses.py`

## Целевой стиль

`handler.py` должен быть коротким и явным:

* `parse_request(event)`
* `match/case` по `Mode`
* lazy import нужного публичного фасада
* delegation

## Минимальный набор mode

На первом шаге завести:

* `HTTP_ACCESS_API`
* `TELEGRAM_WEBHOOK`
* `QUEUE_WORKER`
* `TRIGGER_TIMER`
* `TRIGGER_MORNING`
* `HEALTHCHECK`
* `UNKNOWN`

## Конкретные задачи

1. Вытащить текущую классификацию входов в `parse_request.py`.
2. Нормализовать поля:

   * path;
   * method;
   * source;
   * raw event hints.
3. Сделать `ParsedRequest`.
4. Сделать `unknown_route_response`.
5. Переключить текущую функцию entrypoint на новый `handler.py`.
6. Добавить unit tests на классификацию входов.

## Критерий готовности

Открывая `handler.py`, разработчик сразу видит:

* все режимы;
* куда они идут;
* что worker и triggers — это platform/runtime, а не бизнес-модули.

---

# 5. Кампания D — queue worker как runtime dispatcher, а не бизнес-центр

## Цель

Сохранить queue-механику, но вынести ownership команд в модули.

## Что сделать

Реализовать:

* queue envelope parse;
* command decode;
* явный `match/case` routing по command type;
* delegation в `contexts/*/public.py`.

## Конкретные задачи

1. Создать или нормализовать internal command contract.
2. Зафиксировать список поддерживаемых command types.
3. В `src/platform/runtime/queue_dispatch.py` сделать явный `match/case`.
4. Вынести из worker transport-level concerns:

   * envelope parsing;
   * ack/nack policy;
   * telemetry.
5. Убрать из worker доменную логику.
6. Сделать routing на owning modules:

   * `snapshot`
   * `rendering`
   * `reminders`
   * `telegram_interaction`
   * `attachments`

## Промежуточный переход

На первом этапе допустимо, чтобы `public.py` некоторых модулей временно вызывал старый код, но ownership routing уже должен быть новым.

## Тесты

Нужны тесты на:

* корректный routing известной команды;
* корректную ошибку на неизвестную команду;
* то, что attachment commands уходят только в attachments;
* то, что render commands уходят только в rendering.

## Критерий готовности

Worker знает только:

* как распарсить;
* как определить тип команды;
* в какой модуль отдать исполнение.

---

# 6. Кампания E — trigger orchestration как отдельный слой

## Цель

Отделить schedule/fan-out orchestration от бизнес-модулей.

## Что сделать

Реализовать в `src/platform/runtime/orchestration.py`:

* `handle_timer_trigger`
* `handle_morning_trigger`

## Конкретные задачи

### Для `timer`

Собрать orchestration plan:

* enqueue `update_snapshot`
* enqueue `render_timeline_sheet`
* enqueue `render_designers_sheet`

### Для `morning`

Собрать orchestration plan:

* enqueue `send_reminders`

## Дополнительные требования

* orchestration не должен импортировать тяжёлые доменные модули без нужды;
* orchestration не должен исполнять тяжёлую работу inline;
* orchestration возвращает accepted/status response.

## Тесты

Нужны integration tests:

* `timer` эмитит нужный набор команд;
* `morning` эмитит нужную reminder-команду;
* структура emitted messages соответствует внутреннему queue contract.

## Критерий готовности

Становится ясно, что triggers — не бизнес-модули, а runtime orchestration.

---

# 7. Кампания F — модуль `attachments` как первый полностью оформленный контекст

## Почему начать с него

`attachments` уже похож на отдельную подсистему и даёт лучшую проверку новой архитектуры.

## Цель

Собрать все attachment-сценарии под один ownership.

## Что входит в модуль

* request upload;
* finalize upload;
* attach metadata;
* delete attachment;
* cleanup stale;
* preview generation;
* read/view/download policy;
* signed URLs/storage access.

## Что сделать

Создать структуру:

```text
src/contexts/attachments/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Конкретные задачи

1. Описать `attachment` contracts:

   * commands;
   * queries;
   * DTO;
   * results.
2. Вынести state machine attachment lifecycle в `domain/attachment_state_machine.py`.
3. Вынести preview lifecycle policy.
4. Вынести object storage adapter.
5. Вынести preview converter adapter.
6. Вынести attachment repository adapter.
7. Свести attachment HTTP/admin handlers к публичному фасаду модуля.
8. Свести attachment queue commands к `attachments.public.handle_command`.

## Временный мост

Разрешено временно адаптировать старые функции через thin wrappers, но только внутри нового модуля.

## Тесты

Нужны:

* unit tests на state machine;
* integration tests на request/finalize/delete/preview lifecycle;
* tests на cleanup;
* tests на view/download policy.

## Критерий готовности

Attachment flow полностью читается как единый subsystem.

---

# 8. Кампания G — модуль `reminders`

## Цель

Собрать reminder-домен в один контекст и отделить его от transport/trigger semantics.

## Что входит

* selection logic;
* payload building;
* message styling;
* delivery orchestration;
* counters/retry;
* reminder persistence/state if есть.

## Что сделать

Структура:

```text
src/contexts/reminders/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Конкретные задачи

1. Вынести selection rules в `domain/selection_rules.py`.
2. Вынести reminder message models.
3. Вынести use case `send_reminders.py`.
4. Вынести delivery adapter.
5. Вынести LLM styler adapter.
6. Убрать зависимость reminder flow от trigger meaning `morning`.
7. Оставить `morning` только как orchestration source команды.

## Важный запрет

Нельзя оформлять `morning` как часть reminder domain model.

## Тесты

* кто попадает в reminders;
* как строится payload;
* fallback behavior без стилизации;
* delivery error handling;
* retry semantics, если они бизнес-значимы.

## Критерий готовности

Reminders — отдельный модуль с понятным API и без размазывания по runtime.

---

# 9. Кампания H — разделить `snapshot` и `rendering`

## Цель

Развести ingestion/state update и generation of views.

## Почему это важно

Сейчас они связаны, но архитектурно это разные ownership-зоны:

* snapshot владеет состоянием;
* rendering владеет представлениями.

## Что сделать

Создать два самостоятельных модуля:

* `src/contexts/snapshot/`
* `src/contexts/rendering/`

## Конкретные задачи для `snapshot`

1. Выделить contracts:

   * update commands;
   * query DTO;
   * snapshot results.
2. Вынести normalize logic в domain.
3. Вынести snapshot update use case.
4. Вынести sheets/source adapters.
5. Вынести snapshot repositories.

## Конкретные задачи для `rendering`

1. Выделить render commands.
2. Вынести timeline renderer.
3. Вынести designers renderer.
4. Вынести sheet writer adapter.
5. Сделать зависимость только от публичных snapshot contracts или query facade.

## Важный запрет

`rendering` не должен ходить в приватные внутренности `snapshot`.

## Тесты

* snapshot update flow;
* render flow;
* rendering получает подготовленные данные через контракт, а не прямым доступом к внутренним объектам snapshot.

## Критерий готовности

Можно на уровне кода объяснить разницу между “обновить состояние” и “сгенерировать представление”.

---

# 10. Кампания I — модуль `telegram_interaction`

## Цель

Собрать Telegram intake и interaction logic в один модуль, не смешивая его с reminder domain или runtime worker.

## Что входит

* webhook intake;
* update parsing;
* routing telegram update;
* mapping to internal commands;
* group/user interaction flows.

## Что сделать

Создать структуру:

```text
src/contexts/telegram_interaction/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Конкретные задачи

1. Вынести webhook handler в `public.py`.
2. Вынести update parser adapter.
3. Вынести routing rules в domain/application.
4. Вынести mapping `update -> internal command`.
5. Оставить actual send adapter как infra detail модуля.
6. Убедиться, что Telegram-specific logic не размазана по reminders и runtime.

## Тесты

* webhook classification;
* command mapping;
* group reply enqueue;
* unsupported update fallback.

## Критерий готовности

Telegram взаимодействие читается как самостоятельный interaction module.

---

# 11. Кампания J — модуль `access_api`

## Цель

Собрать frontend-facing HTTP surface, access policy и masking logic в отдельный контекст.

## Что входит

* API handlers для фронта;
* auth/access interpretation;
* masked/open mode;
* response shaping;
* browser-safe DTO.

## Что сделать

Создать структуру:

```text
src/contexts/access_api/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Конкретные задачи

1. Вынести HTTP entry в `handle_http_request`.
2. Выделить access policy.
3. Выделить masking rules.
4. Выделить response DTO assembly.
5. Убедиться, что access_api не знает runtime worker details.
6. Убедиться, что access_api не знает attachment/snapshot/rendering внутренних структур, только публичные contracts/facades.

## Тесты

* masked mode;
* open mode;
* role/access interpretation;
* response shape stability.

## Критерий готовности

Frontend API становится самостоятельным читаемым модулем.

---

# 12. Кампания K — централизованный config и controlled bootstrap

## Цель

Собрать конфигурацию в одном месте и не допустить повторного разрастания глобального bootstrap.

## Что сделать

Создать или нормализовать:

* `src/platform/config/loader.py`
* `src/platform/config/models.py`
* `src/platform/config/secrets.py`

## Конкретные задачи

1. Свести чтение YAML/env в один loader.
2. Вернуть typed config object.
3. Разбить конфиг по срезам:

   * runtime
   * snapshot
   * rendering
   * reminders
   * telegram_interaction
   * attachments
   * access_api
   * infra
   * secrets
4. Перевести модули на получение только своего config slice.
5. Запретить `os.getenv` вне config layer.

## Дополнительная задача

Нормализовать local запуск и pytest setup, чтобы проект поднимался без скрытых приёмов.

## Тесты

* config loading;
* missing secrets/config errors;
* mapping env -> typed settings.

## Критерий готовности

Конфиг больше не размазан по системе.

---

# 13. Кампания L — legacy cleanup и зачистка активного контура

## Цель

Убрать археологию из активной системы.

## Что сделать

1. Определить все неканонические активные code roots.
2. Перенести legacy/old/historical куски в `archive/`.
3. Оставить активный код только в `src/`.
4. Удалить или изолировать compatibility wrappers, если они больше не нужны.
5. Обновить документацию, чтобы legacy не выглядел частью активной архитектуры.

## Важное правило

Если какой-то legacy код пока нельзя удалить, он должен быть:

* явно помечен;
* изолирован;
* не участвовать в новой архитектурной карте как будто это норма.

## Критерий готовности

Корень репозитория визуально описывает текущую систему, а не историю её эволюции.

---

# 14. Кампания M — architecture guardrails и final polish

## Цель

Защитить новую архитектуру от деградации.

## Что сделать

Добавить скрипты/тесты, проверяющие:

* запрет deep imports в чужие контексты;
* запрет импорта из `archive/` в active runtime;
* запрет `os.getenv` вне config layer;
* запрет business logic в `entrypoint`;
* запрет business logic в `platform.runtime`;
* ограничение размера `handler.py`, `public.py`, `module.py`;
* layering rules:

  * `domain` не импортирует adapters/runtime;
  * `application` не лазит в чужие внутренности;
  * `public.py` тонкий;
  * `module.py` содержит wiring, а не предметную логику.

## Дополнительно

Обновить README:

* where to start;
* architecture map;
* module ownership;
* contribution rules.

## Критерий готовности

Архитектура не только красива сейчас, но и защищена от сползания обратно.

---

# 15. Приоритеты, если времени мало

Если нет ресурса делать всё сразу, порядок такой:

## P1 — обязательно

* Кампания A
* Кампания B
* Кампания C
* Кампания D
* Кампания E

Это создаст новый каркас и сохранит сценарии.

## P2 — самые важные модули

* Кампания F (`attachments`)
* Кампания G (`reminders`)
* Кампания H (`snapshot` + `rendering`)

Это даст реальные крупные границы.

## P3 — внешние поверхности

* Кампания I (`telegram_interaction`)
* Кампания J (`access_api`)

## P4 — укрепление

* Кампания K
* Кампания L
* Кампания M

---

# 16. Минимальный целевой скелет файлов

## `src/entrypoint/handler.py`

Обязательный шаблон:

* только parse;
* только `match/case`;
* только lazy imports;
* только delegation.

## `src/platform/runtime/queue_dispatch.py`

Обязательный шаблон:

* parse envelope;
* decode command;
* `match/case` по command type;
* delegation в owning module.

## `src/platform/runtime/orchestration.py`

Обязательный шаблон:

* определить orchestration plan;
* enqueue commands;
* вернуть accepted/status.

## `src/contexts/*/public.py`

Обязательный шаблон:

* взять module singleton/builder;
* делегировать в метод модуля;
* без доменной логики.

## `src/contexts/*/module.py`

Обязательный шаблон:

* собрать локальные зависимости;
* вернуть объект модуля;
* допускается lazy singleton;
* без предметной логики.

---

# 17. Definition of Done по практическому плану

Работа считается выполненной, когда:

* новый entrypoint стал коротким и очевидным;
* queue routing стал явным и ownership-based;
* triggers отделены как orchestration;
* есть оформленные контексты:

  * attachments
  * reminders
  * snapshot
  * rendering
  * telegram_interaction
  * access_api
* модули общаются только через `public.py` и contracts;
* конфиг централизован;
* active code живёт только в `src/`;
* legacy изолирован;
* архитектурные запреты автоматизированы;
* репозиторий читается сверху вниз без археологии.

---



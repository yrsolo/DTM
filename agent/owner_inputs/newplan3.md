````md
# DTM — набор маленьких жёстких кампаний

Этот документ специально сделан **не как большая правильная программа “за всё хорошее”**, а как набор **маленьких, проверяемых, сценарных кампаний**, которые трудно “выполнить полумерой”.

Каждая кампания:
- привязана к одному реальному сценарию;
- бьёт по одному архитектурному обману;
- имеет один новый owning path;
- требует смерти или разжалования старого пути;
- имеет жёсткий `Definition of Done`;
- запрещает “обмазать адаптерами и фасадами”.

## Как этим пользоваться

Не запускать все кампании сразу.  
Делать **по одной**.

После каждой кампании обязательно проверять:
- ownership стал яснее?
- путь сценария стал короче?
- старый путь умер или хотя бы стал deprecated bridge?
- код стало легче читать глазами?
- структура `src` стала лучше, а не сложнее?

Если нет — кампания не завершена.

---

# Кампания 01 — вырезать attachment publication flow из старого transitional контура

## Сценарий
Админ загружает attachment к задаче.  
Attachment проходит async pipeline.  
После завершения attachment становится виден в **основном read-model списка задач**.

## Почему делаем
Сейчас это один из главных реальных сценариев системы, но он очень легко замазывается:
- facade над старым job;
- service над старым service;
- helper с cache invalidation;
- publication point спрятан.

## Цель
Сделать `contexts/attachments` **единственным owning module** для attachment mutation/publication flow.

## Новый единственный путь сценария
- incoming mutation request
- `contexts.attachments.public`
- `contexts.attachments.application`
- `contexts.attachments.domain/adapters`
- publication intent / aftermath metadata
- `platform.runtime` invalidation/publication handling
- attachment виден в основном read-model списка задач

## Что запрещено
Запрещено:
- добавлять новый facade над старым attachment job без разжалования старого пути;
- оставлять старый `jobs/services` attachment flow как нормальный owning path;
- делать прямую очистку чужого cache/read-model из attachments;
- прятать publication semantics в helper/util/service.

## Что должно умереть или стать deprecated bridge
Любой старый путь attachment owning logic в:
- `src/jobs/...`
- `src/services/...`
- `src/entrypoints/...`
должен либо:
- исчезнуть;
- либо стать тонким deprecated bridge с явной задачей на удаление.

## Что показать в отчёте
- новый owning path по файлам;
- старые пути, которые убиты или помечены deprecated;
- где зафиксирован publication point;
- где теперь возникает invalidation/publication intent.

## Definition of Done
Кампания завершена, если:
1. attachment mutation/publication flow проходит через `contexts/attachments`;
2. publication point явно определён как видимость в основном read-model;
3. publication aftermath выражен явно через intent/job/metadata;
4. прямых cross-module cache calls из attachments нет;
5. старый owning path больше не считается нормальным;
6. сценарий читается максимум за 4 перехода.

---

# Кампания 02 — сделать publication aftermath runtime-owned

## Сценарий
После mutation в модуле внешний read-side должен прийти в согласованное состояние.

## Почему делаем
Сейчас это самый частый источник ложной связанности:
- “ну мы всё равно связаны, потому что кэш”
- “давайте просто отсюда почистим там”

Это разрушает модульность.

## Цель
Сделать invalidation/publication aftermath обязанностью `platform.runtime`, а не cross-module знанием.

## Новый единственный путь
- mutation завершён в owning module
- модуль эмитит intent / job / aftermath metadata
- `platform.runtime` обрабатывает invalidation/publication aftermath
- read-side становится согласованным

## Что запрещено
Запрещено:
- прямое удаление/очистка чужого кэша из бизнес-модуля;
- вызов чужих internal cache services;
- спрятанный cache clear в helpers.

## Что должно умереть
Все direct calls вида:
- “модуль А руками инвалидирует read-side модуля Б”
должны исчезнуть или стать deprecated bridges с удалением.

## Что показать в отчёте
- список найденных direct cache cross-calls;
- что заменило каждый из них;
- какой runtime-owned handler теперь обрабатывает aftermath.

## Definition of Done
1. aftermath formalized;
2. intents/jobs/contracts существуют;
3. runtime owns invalidation;
4. cross-module cache direct calls удалены или строго помечены deprecated;
5. affected scenarios читаются яснее.

---

# Кампания 03 — сделать `access_api` хозяином primary read model

## Сценарий
Пользователь открывает интерфейс и получает основной запрос списка задач, который уже содержит:
- данные для карточки;
- attachments;
- всё, что нужно UI без дополнительного card-details request.

## Почему делаем
Сейчас это главный read-сценарий продукта, но его легко оставить в виде:
- набора handler-геттеров;
- транспортного роутера;
- thin alias над старыми хендлерами.

Это не ownership.

## Цель
Сделать `contexts/access_api` реальным владельцем **primary read model**.

## Новый единственный путь
- incoming read request
- `contexts.access_api.public`
- `contexts.access_api.application`
- shaping / masking / response assembly
- read contracts from other modules
- готовый primary read model response

## Что запрещено
Запрещено:
- оставить `access_api` просто набором route-getters;
- читать internal engine/service state других модулей напрямую;
- смешивать read contract с runtime cache mechanics;
- считать, что ownership уже есть только потому, что появился `contexts/access_api`.

## Что должно умереть
Старый owning path основного task-list response в:
- старых handlers,
- случайных info/router кластерах,
- thin wrappers без module ownership

должен исчезнуть или стать deprecated bridge.

## Что показать в отчёте
- где теперь собирается primary read model;
- какие старые handler-centered paths разжалованы;
- где находится shaping/masking;
- как attachments попадают в read-side через published state.

## Definition of Done
1. основной task-list response принадлежит `access_api`;
2. `access_api` не выглядит просто wrapper-ом над legacy handlers;
3. shaping/masking/read-model assembly живут в модуле;
4. attachments попадают через narrow published-state contract;
5. path сценария читается явно и коротко.

---

# Кампания 04 — убрать transport-shaped ownership из `access_api`

## Сценарий
Нужно, чтобы `access_api` читался как модуль read-side, а не как транспортный набор хендлеров.

## Почему делаем
Даже если `access_api` уже завели, он может остаться:
- набором `get_x_handler()`
- transport alias
- местом, где ownership не виден

## Цель
Перевести `access_api` из handler-shaped формы в read-model-owner форму.

## Новый путь
- `access_api.public.handle_http_request`
- `access_api.application.<use_case>`
- `access_api.domain.<response rules>`
- `access_api.contracts.<dto>`

## Что запрещено
- новые `get_*_handler` как главный способ организации;
- транспортно-ориентированная карта вместо сценарно-ориентированной;
- выносить главную смысловую сборку ответа обратно в handlers/router.

## Что должно умереть
Старый handler-centric центр владения внешним read-side.

## Definition of Done
1. по коду видно, что `access_api` владеет read-model сценарием;
2. public фасад не сводится к реэкспорту transport handlers;
3. handler-геттеры перестают быть главным местом понимания API;
4. новый path короче и понятнее.

---

# Кампания 05 — вырезать reminders из notify/service-кластера

## Сценарий
Система отправляет утренние reminders:
- отбирает задачи;
- собирает payload;
- стилизует;
- доставляет.

## Почему делаем
Reminder flow почти всегда замазывается в:
- notify helpers
- delivery service
- jobs
- channel-specific code

И ownership снова расплывается.

## Цель
Сделать `contexts/reminders` единственным owning module reminder business flow.

## Новый путь
- runtime trigger emits reminder command
- `contexts.reminders.public`
- `contexts.reminders.application`
- `contexts.reminders.domain`
- module-local adapters for delivery/styling

## Что запрещено
Запрещено:
- держать selection rules в notify/service-helper слое;
- смешивать reminder business logic с runtime trigger logic;
- тянуть Telegram reserve module как prerequisite reminder ownership;
- создавать “ещё один фасад” над старым reminder job.

## Что должно умереть
Старый notify-centered или job-centered owning path reminder flow.

## Что показать в отчёте
- где теперь lives selection logic;
- где строится payload;
- где styling;
- какие старые notify/service paths разжалованы;
- как `morning` отделён как runtime orchestration.

## Definition of Done
1. `reminders` владеет business flow;
2. `morning` остаётся runtime concern;
3. Telegram reserve code не является центром reminder логики;
4. старый notify path не считается нормальным;
5. сценарий прослеживается коротко.

---

# Кампания 06 — сделать `morning` trigger чистой orchestration-веткой

## Сценарий
Утром runtime инициирует reminders.

## Почему делаем
Очень легко смешать:
- trigger semantics
- scheduling
- reminder business rules

И тогда runtime начинает владеть доменом.

## Цель
Оставить `morning` только runtime orchestration.

## Новый путь
- trigger enters runtime
- runtime emits reminder command
- `reminders` выполняет доменную работу

## Что запрещено
- писать selection/payload logic в trigger layer;
- считать `morning` частью reminder domain.

## Что должно умереть
Любой старый path, где `morning`-ветка делает заметную доменную работу inline.

## Definition of Done
1. `morning` только оркестрирует;
2. reminders делает домен;
3. код clearly split;
4. нет hidden business logic в runtime trigger path.

---

# Кампания 07 — вырезать `rendering` из snapshot internals

## Сценарий
Система обновляет snapshot и строит render projections:
- timeline
- представление по дизайнерам
- другие выходные представления

## Почему делаем
Это самый опасный boundary.
Если `rendering` продолжает читать snapshot engine internals, модульность фиктивна.

## Цель
Сделать `rendering` зависимым только от:
- `snapshot.public`
- `snapshot.contracts`

## Новый путь
- runtime/queue dispatch
- `contexts.rendering.public`
- rendering use case
- narrow snapshot query contract
- render output

## Что запрещено
- direct imports из snapshot internals;
- engine leakage;
- capability-wrapper над engine как финальное решение;
- любые “временные” обходы без strict deprecation.

## Что должно умереть
Прямые internal snapshot reads из rendering path.

## Что показать в отчёте
- список removed imports/dependencies;
- какой contract заменил internal dependency;
- какие тесты защищают boundary.

## Definition of Done
1. `rendering` не знает snapshot internals;
2. only narrow contracts remain;
3. old internal access path удалён или deprecated с дедлайном;
4. guardrails/tests добавлены.

---

# Кампания 08 — превратить `snapshot` из engine-фасада в настоящий модуль

## Сценарий
Система делает:
- ingestion
- normalization
- snapshot update
- snapshot query

## Почему делаем
Частый обман: завести `contexts/snapshot`, но реально продолжать жить через `build_snapshot_engine(...)`.

## Цель
Сделать `snapshot` не фасадом над engine, а модулем, где engine перестаёт быть архитектурным центром.

## Новый путь
- `contexts.snapshot.public`
- `contexts.snapshot.application`
- `contexts.snapshot.domain`
- `contexts.snapshot.adapters`

## Что запрещено
- светить engine наружу;
- делать capability wrappers как финальную форму;
- оставлять `get_snapshot_engine()` как ключевой внешний путь.

## Что должно умереть
Engine-centric внешний path.

## Что показать в отчёте
- где раньше engine был главным центром;
- что стало новым owning path;
- какие внешние места больше не знают engine.

## Definition of Done
1. snapshot публично читается как модуль, а не как engine facade;
2. engine не светится как внешний архитектурный центр;
3. update/query paths идут через module contracts;
4. old engine-shaped path разжалован.

---

# Кампания 09 — убрать domain ownership из bootstrap для одного конкретного сценария

## Сценарий
Выбрать один реальный сценарий, например:
- attachment publication
- reminders send
- render timeline

## Почему делаем
Большой bootstrap слишком долго остаётся скрытым мозгом.
Но “почистить весь bootstrap” — слишком широкая и беспомощная задача.

## Цель
Забрать у bootstrap ownership **одного конкретного сценария** и перевести его в module-local builder.

## Новый путь
- global bootstrap only delegates/shared infra
- scenario assembled in `contexts/<module>/module.py`

## Что запрещено
- делать новую красивую функцию в bootstrap вместо реального переноса;
- оставлять bootstrap единственным местом, где понятен сценарий;
- считать partial delegation победой, если old assembly still rules.

## Что должно умереть
Один конкретный domain-specific builder path в bootstrap.

## Что показать в отчёте
- какой именно сценарий перестал собираться в bootstrap;
- где теперь живёт local builder;
- что убрали из bootstrap.

## Definition of Done
1. один конкретный сценарий ушёл из bootstrap;
2. `module.py` реально собирает этот сценарий;
3. bootstrap больше не нужен для понимания этого flow;
4. old bootstrap path removed/deprecated.

---

# Кампания 10 — убрать fake modularity из `contexts/*` для одного модуля

## Сценарий
Выбрать один модуль:
- attachments
- reminders
- snapshot
- access_api

## Почему делаем
Частая полумера: есть `public.py`, `module.py`, красивая папка, но всё внутри просто отправляется в старый cluster.

## Цель
Сделать так, чтобы выбранный context перестал быть фасадом над legacy/transitional core.

## Новый путь
- public
- module
- application
- domain
- adapters

и старый path больше не является главным.

## Что запрещено
- ограничиться переименованием/re-export;
- оставить старый job/service cluster как фактический owner;
- сказать “ownership перенесён”, если путь выполнения остался старым.

## Что должно умереть
Один конкретный fake-modular path.

## Definition of Done
1. context реально владеет сценарием;
2. старый cluster не является обязательным для понимания flow;
3. public/module не thin decorative bridge;
4. код внутри контекста стал смысловым центром.

---

# Кампания 11 — вычистить один конкретный competing center из `src`

## Сценарий
Не бизнес-сценарий, а structural scenario:
убрать один старый архитектурный центр из активной карты проекта.

Например:
- `src/jobs` как active center
- `src/services`
- `src/entrypoints_adapters`
- `src/worker`
- `src/notify`

## Почему делаем
Пока в `src` визуально несколько равноправных центров, красоты не будет.

## Цель
Разжаловать один конкретный competing center:
- либо сделать его внутренностью модулей/platform;
- либо перевести в deprecated;
- либо увести в archive.

## Что запрещено
- косметически оставить всё как есть;
- переименовать без смены роли;
- оставить зону как “ну пока ещё можно”.

## Что должно умереть
Один top-level competing center в active architecture.

## Что показать в отчёте
- какой center разжалован;
- куда ушёл активный код;
- что стало новой нормой;
- какой guardrail запрещает возврат.

## Definition of Done
1. один competing center больше не является active canonical area;
2. `src` стал чище глазами;
3. есть guardrail против возврата;
4. docs map updated.

---

# Кампания 12 — жёстко зафиксировать `src` как красивую карту

## Сценарий
Это structural aesthetics campaign.

## Почему делаем
Твоя цель — не только модульность, но и **красота репозитория как pet project**.

## Цель
Привести active `src` к виду, где сразу видно:

```text
src/
  entrypoint/
  platform/
  contexts/
  shared/
````

и не видно свалки конкурирующих active зон.

## Что запрещено

* создавать новые top-level active dirs вне этих четырёх групп;
* сохранять старые исторические зоны как равноправные;
* объяснять структуру фразой “тут просто исторически так”.

## Что должно умереть

Любая новая или старая top-level active зона, не укладывающаяся в канон.

## Definition of Done

1. tree `src` эстетичен;
2. active map читается сразу;
3. старые зоны разжалованы/архивированы;
4. структура сама обучает архитектуре.

---

# Кампания 13 — изолировать Telegram как reserve capability

## Сценарий

Telegram interaction не является активным продуктовым фокусом, но удалять его не хочется.

## Почему делаем

Сейчас опасность в том, что Telegram может:

* течь в reminders;
* течь в runtime;
* течь в общую архитектуру;
* и при этом отнимать силы без реальной пользы.

## Цель

Перевести Telegram в режим:

* isolated
* reserve
* low-maintenance
* non-blocking for active architecture

## Новый путь

* `contexts.telegram_interaction` как isolated reserve zone
* active modules не зависят от его полной полировки

## Что запрещено

* тратить disproportionate effort на вылизывание reserve module;
* размазывать Telegram code по active modules;
* делать reminders зависимыми от полного Telegram refactor.

## Что должно умереть

Telegram как скрытый architectural center.

## Definition of Done

1. Telegram isolated;
2. reminders независимы;
3. reserve status documented;
4. активная карта проекта не ломается Telegram-кодом.

---

# Кампания 14 — удалить один конкретный legacy/deprecated bridge

## Сценарий

Выбрать один bridge, который уже давно “временно” живёт.

## Почему делаем

Главная причина бесконечной переходности — bridges живут вечно.

## Цель

Физически удалить один bridge, а не просто оставить TODO.

## Что запрещено

* заменить старый bridge новым bridge;
* оставить удаление “на потом”;
* считать это неважным.

## Definition of Done

1. один bridge реально удалён;
2. путь сценария короче;
3. новые тесты/guardrails не дают его вернуть незаметно.

---

# Кампания 15 — добавить guardrail под один конкретный архитектурный обман

## Сценарий

Выбрать один уже замеченный тип деградации:

* `rendering` импортирует snapshot internals
* cross-module cache calls
* new top-level active dir in `src`
* new bootstrap domain assembly
* context facade over old cluster without old-path death

## Почему делаем

Без guardrails старый стиль всегда прорастает обратно.

## Цель

Сделать так, чтобы конкретный архитектурный обман больше нельзя было повторить незаметно.

## Definition of Done

1. test/script exists;
2. old violation detected by it;
3. rule documented;
4. future regressions caught automatically.

---

# Рекомендуемый порядок этих маленьких кампаний

Если делать по уму, я бы шёл так:

1. **Кампания 01** — attachment publication flow
2. **Кампания 02** — publication aftermath runtime-owned
3. **Кампания 03** — access_api owner of primary read model
4. **Кампания 04** — убрать transport-shaped ownership из access_api
5. **Кампания 05** — reminders as real module
6. **Кампания 06** — clean morning trigger
7. **Кампания 07** — rendering out of snapshot internals
8. **Кампания 08** — snapshot not engine-facade
9. **Кампания 09** — remove one scenario from bootstrap
10. **Кампания 10** — kill fake modularity in one context
11. **Кампания 11** — remove one competing center from src
12. **Кампания 13** — isolate Telegram reserve module
13. **Кампания 14** — delete one real deprecated bridge
14. **Кампания 15** — add one strong guardrail

---

# Главное правило постановки этих кампаний агенту

Никогда не давать задачу так:

* “улучши модульность”
* “сделай модуль настоящим”
* “приведи к красивой архитектуре”
* “доведи до канона”

Всегда давать так:

* вот один сценарий
* вот старый path
* вот новый owning path
* вот что запрещено
* вот что должно умереть
* вот как проверить done

---

# Универсальный шаблон для любой следующей маленькой кампании

## Название

Одно узкое действие.

## Сценарий

Один реальный сценарий.

## Архитектурный обман

Что именно сейчас делает модульность фальшивой.

## Новый owning path

Какой путь должен стать единственным.

## Запреты

Какие полумеры нельзя делать.

## Что должно умереть

Какие старые path/cluster/bridge должны исчезнуть или стать deprecated.

## Что показать в отчёте

Список файлов, removed paths, changed ownership.

## Definition of Done

Проверяемые признаки в коде и глазами.

---

# Финальный критерий качества

После каждой кампании открой:

* верхний handler
* relevant `contexts/<module>/public.py`
* relevant `contexts/<module>/module.py`
* главный use case этого сценария
* дерево `src`

и спроси:

1. Ownership стал очевиднее?
2. Путь сценария стал короче?
3. Старый path умер?
4. Код стало приятнее читать глазами?
5. Структура стала красивее?

Если хотя бы на 2 вопроса ответ “нет”, кампания не удалась.

```
```

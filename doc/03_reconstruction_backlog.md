# Backlog реконструкции (подробный план)

## Цели реконструкции
- Сохранить 100% текущей функциональности.
- Убрать архитектурную связанность и сделать систему расширяемой.
- Создать безопасный контур разработки на тестовой таблице.
- Подготовить базу для переноса визуализации из Google Sheets в отдельный интерфейс.
- Целевая модель описана в: `doc/04_target_architecture.md`.
- Риск-реестр: `doc/05_risk_register.md`.
- ADR-реестр: `doc/06_adrs.md`.
- Security-аудит публикации: `doc/07_publication_security_audit.md`.
- Runbook публикации: `doc/08_public_repo_bootstrap.md`.
- Git workflow: `doc/09_git_workflow.md`.

## Принцип выполнения
- Только поэтапная миграция (strangler pattern), без "big bang rewrite".
- Каждый этап завершать валидацией на реальных данных.
- Новую логику включать через флаги/режимы, а не заменять одномоментно.
- На каждый этап обязателен rollback-сценарий (откат не более 5-10 минут).

## Definition of Done (для каждого спринта)
- Код + миграции (если есть) + обновленная документация.
- Демо-сценарий прогона на тестовой среде.
- Артефакты сравнения baseline/new (таблицы, diff, логи).
- Метрики качества этапа (ошибки, latency, стабильность).

## SLO/SLI (эксплуатационный минимум)
- SLI `sync_success_rate`: доля успешных прогонов синка.
- SLI `reminder_delivery_rate`: доля успешных доставок сообщений.
- SLI `pipeline_duration_p95`: p95 времени полного прогона.
- SLO стартово:
  - `sync_success_rate >= 99%`
  - `reminder_delivery_rate >= 98%`
  - `pipeline_duration_p95 <= 10 min`

## Decision log (ADR)
- Ключевые архитектурные решения фиксируются в ADR:
  - выбор архитектурного стиля;
  - выбор хранилища;
  - стратегия миграции Sheets -> DB/UI;
  - стратегия idempotency и retry.

---

## Этап 0. Организация локальной тестовой системы (первый приоритет)

## 0.1. Явно зафиксировать тестовый контур
- Подтвердить использование `SOURCE_SHEET_NAME`/`TARGET_SHEET_NAME` как дефолтного dev-контура.
- Ввести `ENV=dev/test/prod`.
- Вынести настройки окружений в отдельные секции/файлы (`.env.dev`, `.env.prod`).

Критерий готовности:
- локальный запуск не может писать в боевую таблицу при `ENV=dev`.

## 0.2. Разделить таблицу чтения и таблицу записи
- Добавить 2 конфигурации:
  - `SOURCE_SHEET_NAME` (откуда читать задачи/людей),
  - `TARGET_SHEET_NAME` (куда писать `Дизайнеры/Календарь/Задачи`).
- На dev-среде включить сценарий:
  - чтение из актуальной рабочей таблицы;
  - запись только в тестовую таблицу.
- Обновить `GoogleSheetInfo`/планировщик так, чтобы read/write таблицы могли различаться без хака в коде.

Критерий готовности:
- один запуск формирует выходные листы в `TARGET`, не изменяя `SOURCE`.

Статус:
- реализовано в текущем коде (`GoogleSheetPlanner` + `SOURCE_SHEET_INFO`/`SHEET_INFO`).

## 0.3. Режимы прогона и dry-run
- Добавить режим:
  - `--mode sync-only` (без Telegram),
  - `--mode reminders-only`,
  - `--dry-run` (без записи в Google API, только лог diff).

Критерий готовности:
- можно локально проверить итог без фактической записи.

## 0.4. Базовая валидация результата "как есть"
- Снять baseline-скрин/экспорт целевых листов после текущего кода.
- После каждого изменения сравнивать:
  - количество строк/столбцов;
  - значения ключевых ячеек;
  - наличие заметок и цветов.

Критерий готовности:
- есть повторяемый чеклист "ничего не сломали".

Статус:
- реализован базовый artifact flow: `agent/capture_baseline.py` + `doc/02_baseline_validation_and_artifacts.md`.

## 0.5. Gate публикации и безопасность репозитория
- Ввести pre-commit проверку на секреты (`detect-secrets` или `gitleaks`).
- Провести sanitation репозитория (ключи, токены, прокси-креды, личные данные).
- Добавить security-checklist перед публикацией.

Критерий готовности:
- репозиторий проходит secret-scan без критичных находок.

Статус:
- gate активен через pre-commit `detect-secrets` + baseline `.secrets.baseline`, подтверждается smoke-командой `pre-commit run detect-secrets --all-files`.

---

## Этап 1. Стабилизация данных и контрактов
- Ввести модели данных (Pydantic/dataclass) для:
  - `TaskRaw`, `TaskParsed`, `Person`, `ReminderMessage`.
- Валидировать обязательные колонки и типы при чтении листов.
- Явно обрабатывать ошибки данных (пустые даты, кривые тайминги, нет chat_id).

Критерий готовности:
- ошибки входных данных не приводят к падению всего пайплайна.

Статус:
- стартован инкремент Stage 1: добавлена валидация обязательных колонок задач в `core/repository.py` (DTM-8).
- выполнен следующий инкремент Stage 1: hardening `TimingParser.parse` для null/non-string payload и нормализация nullable текстовых полей `Task` (DTM-9).
- выполнен инкремент Stage 1 по people-контрактам: null-safe нормализация `Person`, безопасный mapping `PeopleManager`, исправление `get_designers` (DTM-10).
- выполнен runtime-фикс reminder-контура: совместимый `httpx` proxy setup + unicode-safe logging для dry-run напоминаний (DTM-11).
- выполнен контрактный scaffold Stage 1: typed row-контракты для Task/Person (`core/contracts.py`) и перевод row mapping в `repository/people` на эти контракты (DTM-12).
- выполнен guardrail-инкремент Stage 1: required-header валидация tasks/people через метаданные typed contracts + fail-fast ошибки с контекстом листа (DTM-13).
- выполнен инкремент Stage 1 по taxonomy ошибок качества данных: добавлены typed исключения (`DataQualityError`, `MissingRequiredColumnsError`) и унифицирована диагностика missing-header для task/people загрузчиков (DTM-14).
- выполнен инкремент Stage 1 по row-level policy: malformed task/person rows обрабатываются fail-soft (skip + `RowValidationIssue` диагностика) без падения всего пайплайна (DTM-16).
- выполнен инкремент Stage 1 по timing diagnostics: ошибки парсинга тайминга учитываются структурированно (`TimingParseIssue`) и отражаются в row-level accounting без фатальной остановки пайплайна (DTM-17).
- выполнен инкремент Stage 1 по quality artifact surfacing: локальные прогоны и baseline capture формируют структурированный `quality_report.json` с агрегированными Stage 1 diagnostics (DTM-18).
- выполнен инкремент Stage 1 по test-safe reminder execution: для тестового контура добавлен mock external mode (`OpenAI` + `Telegram`) без внешних side effects (DTM-15).

---

## Этап 2. Декомпозиция по слоям
- Выделить слои:
  - `domain` (чистые правила),
  - `application` (use-cases),
  - `infrastructure` (Google/Telegram/OpenAI),
  - `interfaces` (CLI/Cloud handler).
- Убрать прямые вызовы Google API из доменных классов.

Критерий готовности:
- основная бизнес-логика тестируется без внешних API.

Статус:
- Stage 2 kickoff started: layer boundary inventory and dependency map completed (`doc/10_stage2_layer_inventory.md`, DTM-19).
- выполнен Stage 2 scaffold-инкремент `S2-SLICE-01`: выделен bootstrap boundary для сборки зависимостей планировщика (`core/bootstrap.py`) и подключена dependency injection инициализация в `main.py`/`core/planner.py` (DTM-20).
- выполнен Stage 2 application-инкремент: orchestration use-cases (`resolve_run_mode`, pipeline branches) вынесены из `main.py` в `core/use_cases.py` с сохранением run-mode поведения (DTM-21).
- выполнен Stage 2 infrastructure-инкремент: добавлены adapter contracts (`core/adapters.py`) и явная инъекция Telegram/OpenAI адаптеров в reminder/bootstrap wiring (DTM-22).

---

## Этап 3. Рефакторинг календарей и визуализации в Sheets
- Унифицировать генерацию структур для `Календарь` и `Задачи`.
- Вынести "рендер в таблицу" в отдельный адаптер.
- Сделать единые правила цветов/подписей/нотов.

Статус:
- Stage 3 started: shared render cell-contract scaffold introduced (`core/render_contracts.py`) and integrated into `TaskCalendarManager` rendering flow (`DTM-23`).
- Stage 3 alignment increment completed: task-calendar renderer payload/style branches normalized through helper methods over shared render contract (`DTM-24`).
- Stage 3 adapter extraction increment completed: sheet write operations of `TaskCalendarManager` moved behind `SheetRenderAdapter` boundary with `ServiceSheetRenderAdapter` and bootstrap DI wiring (`DTM-25`).
- Stage 3 adapter extraction continued: `CalendarManager` write path moved behind `SheetRenderAdapter` boundary with bootstrap DI wiring (`DTM-26`).
- Stage 3 parity increment completed: `CalendarManager` header/date/body payload assembly normalized through helper methods over `RenderCell` (`DTM-27`).
- Stage 3 harness increment completed: adapter dry-run assertion script added (`agent/render_adapter_smoke.py`, `DTM-28`).
- Stage 3 close-out increment completed: `TaskManager` designers-sheet write path moved to `SheetRenderAdapter` + `RenderCell` with bootstrap DI renderer wiring (`DTM-29`).
- Stage 3 close-out coverage increment completed: manager-level adapter-path assertions added to `agent/render_adapter_smoke.py` for active `TaskManager` and `CalendarManager` flows (`DTM-30`).
- Stage 3 legacy disposition increment completed: unused `TaskCalendarManagerOld` path and obsolete global `write_cur_time` helper removed from `core/manager.py` (`DTM-31`).

Критерий готовности:
- обе визуализации строятся через единый промежуточный формат.

---

## Этап 4. Рефакторинг reminder-пайплайна
- Разделить:
  - генератор фактов по задачам,
  - генератор черновика,
  - LLM-enhancer,
  - отправщик в Telegram.
- Добавить fallback:
  - если OpenAI недоступен, отправлять валидный черновик.
- Добавить защиту от дублей отправки.

Критерий готовности:
- напоминания отправляются стабильно даже при деградации внешних сервисов.

Статус:
- Stage 4 kickoff started: fallback hardening for empty/unavailable OpenAI enhancer response with draft-message delivery preservation (`DTM-32`).
- Stage 4 idempotency increment completed: in-run duplicate-delivery guard added for reminder sends with deterministic smoke verification (`DTM-33`).
- Stage 4 decomposition increment completed: reminder pipeline split into explicit internal steps (context/draft-enhance/delivery) with preserved behavior and deterministic smoke verification (`DTM-34`).
- Stage 4 parallel enhancement increment completed: OpenAI reminder enhancer path now runs in parallel fan-out with bounded concurrency and reusable client, with deterministic parallel smoke verification (`DTM-35`).
- Stage 4 observability increment completed: reminder delivery outcome counters integrated into runtime logs and planner quality report with deterministic counters smoke verification (`DTM-36`).
- Stage 5 kickoff increment completed: derived reminder SLI metrics (`delivery_rate`, `failure_rate`, attemptable/attempted counters) integrated into quality report summary with deterministic formula smoke verification (`DTM-37`).
- Stage 5 kickoff increment completed: risk register aligned to implemented reminder/API mitigations with explicit retry-policy stance and ownership (`DTM-38`).

---

## Этап 5. Наблюдаемость и эксплуатация
- Структурные логи по каждому шагу пайплайна.
- Метрики:
  - число обработанных задач,
  - число отправленных сообщений,
  - число ошибок по интеграциям.
- Уведомления о критических сбоях в отдельный тех-чат.

Критерий готовности:
- можно быстро понять "что сломалось и где".

---

## Этап 5.1. Риск-реестр и mitigation
- Вести risk register:
  - риск;
  - вероятность;
  - влияние;
  - mitigation;
  - owner.
- Отдельно контролировать риски:
  - квоты Google API;
  - timezone/календарные ошибки;
  - дубли отправки Telegram;
  - деградация OpenAI.

Критерий готовности:
- по каждому high-risk есть конкретный mitigation и owner.

---

## Этап 6. Подготовка к новой платформе визуализации
- Ввести read-model API (единый JSON-слепок задач/этапов/дедлайнов).
- Оставить Google Sheets как "витрину", но не как единственный формат.
- Спроектировать новую UI-витрину (web):
  - фильтры по дизайнеру/бренду/статусу;
  - timeline/gantt;
  - история изменений и комментарии.

Критерий готовности:
- данные пригодны для фронтенда без повторного парсинга таблиц.

---

## Предлагаемая очередность спринтов
1. Спринт 1: Этап 0.1-0.2 (dev-контур + read/write split).
2. Спринт 2: Этап 0.3-0.5 (режимы прогонов + baseline + security gate).
3. Спринт 3: Этап 1 (контракты данных).
4. Спринт 4: Этап 2 (слоистая архитектура + ADR для ключевых решений).
5. Спринт 5: Этап 3 (рефакторинг календарей + contract tests адаптеров).
6. Спринт 6: Этап 4 (refactor reminders + idempotency).
7. Спринт 7: Этап 5-5.1 (observability + risk register + SLO/SLI).
8. Спринт 8: Этап 6 (подготовка UI миграции и read-model API).

## Стратегия cutover
- Шаг 1: shadow-run (новый пайплайн без влияния на боевой результат).
- Шаг 2: ограниченный запуск (10%).
- Шаг 3: частичный запуск (50%).
- Шаг 4: полный запуск (100%).
- На каждом шаге есть стоп-критерии и rollback.

## Что делать сразу после утверждения backlog
1. Зафиксировать и протестировать текущую реализацию `SOURCE_SHEET_NAME`/`TARGET_SHEET_NAME` на smoke-тестах.
2. Прогнать локально: read из рабочей, write в `Спонсорские ТНТ ТЕСТ`.
3. Зафиксировать baseline результата и дифф.
4. Подключить сканер секретов и прогнать sanitation репозитория.
5. Создать demo-dataset без персональных данных для портфолио.

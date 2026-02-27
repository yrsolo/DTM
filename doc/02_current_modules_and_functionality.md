# Модули и текущий функционал

## Точки входа

## `main.py`
- Определяет режим запуска (`timer`, `morning`, `test`) по event/trigger.
- Создает bootstrap-зависимости планировщика через `core/bootstrap.py` и передает их в `GoogleSheetPlanner`.
- Делегирует orchestration flow в application use-cases (`core/use_cases.py`).
- В режиме `timer/test`:
  - обновляет данные;
  - перерисовывает листы `Задачи`, `Календарь`, `Дизайнеры`.
- В режиме `morning/test`:
  - формирует и отправляет напоминания.

## `index.py`
- Обертка для Yandex Cloud.
- Вызывает `main(event=...)`.
- Ловит исключения и шлет подробности в Telegram лог-чат.

## Конфигурация

## `config/constants.py`
- Токены/секреты из `.env`.
- Режим окружения:
  - `ENV` (`dev`/`test`/`prod`);
  - optional override из `.env.<ENV>` при наличии файла.
- Разделение таблиц:
  - `SOURCE_SHEET_NAME` (чтение),
  - `TARGET_SHEET_NAME` (запись),
  - `SHEET_NAMES` (карта листов).
- Guard безопасности:
  - при `STRICT_ENV_GUARD=1` и `ENV=dev/test` `SOURCE_SHEET_NAME` и `TARGET_SHEET_NAME` обязаны различаться (fail-fast на старте).
- Маппинги колонок задач и людей (`TASK_FIELD_MAP`, `PEOPLE_FIELD_MAP`).
- Правила статуса по цвету (`COLOR_STATUS`).
- Палитра цветов для записи в таблицы (`COLORS`).
- Промпт персонажа для GPT (`HELPER_CHARACTER`), модель (`MODEL`), прокси (`PROXY_URL` -> `PROXIES`).
- Триггеры облачных событий (`TRIGGERS`).

## Домен и обработка задач

## `core/repository.py`
- `TimingParser`: парсинг поля "Тайминг" в словарь `date -> stages`.
- `Task`: объект задачи, ленивый доступ к распарсенному таймингу.
- `GoogleSheetsTaskRepository`:
  - читает задачи из Google Sheets;
  - читает цвет ячеек первой колонки;
  - вычисляет `color_status`;
  - нормализует поле дизайнеров;
  - строит `Task`.

## `core/manager.py`
- `TaskManager`:
  - обновление коллекции задач;
  - генерация листа `Дизайнеры`.
- `TaskTimingProcessor`:
  - преобразование задач в структуру тайминга для календарей.
- `CalendarManager`:
  - формирование и запись листа `Календарь`.
- `TaskCalendarManager`:
  - основной текущий рендер листа `Задачи` через `all_tasks_to_sheet()` (структура по дизайнерам + таймлайн).

## Люди и уведомления

## `core/people.py`
- `Person`, `Designer`.
- `PeopleManager`:
  - загрузка справочника людей с листа `Люди`;
  - поиск сотрудника по имени.

## `core/reminder.py`
- `TelegramNotifier`: отправка сообщений в Telegram + логирование.
- `AsyncOpenAIChatAgent`: вызов OpenAI для улучшения текста.
- `Reminder`:
  - расчет дат "сегодня/следующий рабочий день";
  - группировка задач по дизайнерам;
  - сбор черновика;
  - улучшение текста через OpenAI;
  - отправка по chat_id сотрудника.
  - fallback-поведение: если OpenAI enhancer вернул пустой/недоступный ответ, используется draft-сообщение вместо пустой отправки.
  - idempotency guard: повторная отправка идентичного сообщения тому же designer/chat в рамках одного run-cycle пропускается.
  - test-safe режим: при `mock_external` используется `MockOpenAIChatAgent`, а Telegram-отправка пропускается без внешних вызовов.

## `core/bootstrap.py`
- Stage 2 scaffold-модуль для сборки зависимостей планировщика (`build_planner_dependencies`).
- Централизует wiring `GoogleSheetsService` / managers / repository / reminder stack вне `GoogleSheetPlanner`.

## `core/use_cases.py`
- Stage 2 application-layer use-cases:
  - `resolve_run_mode(...)` для определения режима выполнения из аргументов/event;
  - `run_planner_use_case(...)` для orchestration веток sync/reminder и сборки quality report.

## `core/adapters.py`
- Stage 2 adapter boundary контракты для внешних интеграций:
  - `ChatAdapter` (LLM/OpenAI),
  - `MessageAdapter` (Telegram),
  - `LoggerAdapter`,
  - `NullLogger` (без side effects).

## Инфраструктура и утилиты

## `utils/service.py`
- Низкоуровневый клиент Google Sheets/Drive:
  - поиск spreadsheet id по имени;
  - чтение значений в DataFrame;
  - чтение цветов ячеек;
  - batch update ячеек;
  - очистка диапазонов.

## `utils/func.py`
- Работа с цветами, парсинг диапазонов, фильтрация стадий.

## Фактический поток данных
1. Чтение `ТАБЛИЧКА` + цвета строк из `SOURCE_SHEET_NAME`.
2. Нормализация/парсинг задач.
3. Генерация производных представлений и запись в `TARGET_SHEET_NAME`:
   - `Дизайнеры`
   - `Календарь`
   - `Задачи`
4. Чтение `Люди` из `SOURCE_SHEET_NAME`.
5. Генерация и отправка утренних сообщений.

## Узкие места для реконструкции
- Смешение доменной логики, форматирования и API-адаптеров.
- Нет регрессионного тестового контура на реальных данных таблицы.

## 2026-02-27 update
- `GoogleSheetsTaskRepository` now validates required task columns before mapping rows to `Task` objects.
- If required headers are missing, repository raises explicit `ValueError` with column names and sheet reference.
- `TimingParser.parse` now handles nullable/non-string timing payloads safely and exits early on empty input.
- `Task` now normalizes nullable text fields (`brand`, `format_`, `project_name`, `customer`, `designer`, `status`, `color_status`, `name`, `raw_timing`) before downstream usage.
- `Person`/`PeopleManager` now normalize nullable people fields and use safer mapping (`core/people.py`), including fixed preloaded people map and corrected `get_designers()` return type.
- `core/reminder.py` reminder runtime path is updated for current `httpx` compatibility (`proxy=` with sanitized URL) and unicode-safe console logging.
- Added `core/contracts.py` typed row contracts (`TaskRowContract`, `PersonRowContract`) and switched repository/people row mapping through these non-breaking contract objects.
- Required-sheet-header validation now derives from contract metadata (`required_columns`) for both tasks and people, with fail-fast typed data-quality errors including sheet context.
- Added `core/errors.py` typed data-quality taxonomy (`DataQualityError`, `MissingRequiredColumnsError`) for sheet-contract failures.
- Task/people required-header checks now raise `MissingRequiredColumnsError` (ValueError-compatible) with unified diagnostics format and sheet context.
- Row-level fail-soft policy added for malformed task/people rows: loaders skip invalid rows and record `RowValidationIssue` diagnostics (`row_issues`) instead of failing whole load.
- `TimingParser` now keeps structured diagnostics (`TimingParseIssue`, `parse_issues`, `total_parse_errors`), and task loader records timing-parse error counts into row-level issues without stopping the pipeline.
- `GoogleSheetPlanner.build_quality_report()` now surfaces structured Stage 1 diagnostics; `main.py` prints quality summary and `local_run.py --quality-report-file` can persist JSON artifacts.
- Added reminder external-call mock controls for test runs: `main.py` auto-enables `mock_external` for `mode=test`, `local_run.py` supports explicit `--mock-external`, and reminder flow skips real OpenAI/Telegram calls in this mode.
- Stage 2 scaffold: planner dependency construction moved into explicit bootstrap boundary (`core/bootstrap.py`), and `main.py` now uses injected dependencies when constructing `GoogleSheetPlanner`.
- Stage 2 application use-case extraction: orchestration ветки выполнения вынесены из `main.py` в `core/use_cases.py`.
- Stage 2 infra adapter extraction: reminder/bootstrap flow uses explicit external adapter contracts (`core/adapters.py`) with injected Telegram/OpenAI implementations.
- Stage 4 fallback hardening: reminder pipeline now enforces draft fallback when enhancer output is empty/unavailable and includes deterministic local smoke `agent/reminder_fallback_smoke.py`.
- Stage 4 idempotency increment: reminder send path tracks in-run delivery keys and skips duplicate sends; deterministic smoke added in `agent/reminder_idempotency_smoke.py`.
- Stage 4 decomposition increment: reminder flow decomposed into explicit helper steps (context collection, per-designer message build, delivery resolution, send execution) while preserving `get_reminders`/`send_reminders` external contract.
- Stage 4 parallel enhancement increment: reminder enhancer calls now fan out in parallel via `asyncio.gather` with bounded concurrency (`enhance_concurrency` semaphore), and OpenAI/httpx client is reused per agent instance; deterministic parallel smoke added in `agent/reminder_parallel_enhancer_smoke.py`.
- Stage 4 observability increment: reminder send path now emits structured delivery counters (`sent/skipped/error`) and planner quality report includes `reminder_delivery_counters` with summary fields (`reminder_sent_count`, `reminder_send_error_count`); deterministic smoke added in `agent/reminder_delivery_counters_smoke.py`.
- Stage 5 SLI kickoff increment: planner quality report now derives reminder SLI metrics (`reminder_delivery_attemptable_count`, `reminder_delivery_attempted_count`, `reminder_delivery_rate`, `reminder_failure_rate`) from delivery counters; deterministic formula smoke added in `agent/reminder_sli_summary_smoke.py`.

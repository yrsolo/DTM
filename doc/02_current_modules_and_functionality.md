# Модули и текущий функционал

## Точки входа

## `main.py`
- Определяет режим запуска (`timer`, `morning`, `test`) по event/trigger.
- Создает `GoogleSheetPlanner`.
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
- `TaskCalendarManagerOld`:
  - сохранена легаси-реализация табличного рендера `Задачи` как fallback/референс.

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

# DTM-35: TSK-038 Stage 4 parallel OpenAI reminder enhancement with bounded concurrency

## Context
- В текущем `Reminder.get_reminders()` улучшение сообщений выполняется последовательно по дизайнерам.
- OpenAI API latency заметна, при нескольких дизайнерах это увеличивает общее время reminder-ветки.
- Требуется реальная параллельная обработка с ограничением конкуренции, без изменения бизнес-логики fallback/idempotency.

## Goal
- Включить параллельный enhancer-path по дизайнерам через async gather + bounded concurrency.
- Сохранить совместимость текущих entrypoint и существующих smoke-проверок.

## Non-goals
- Не менять формат текстов, правила reminder контента и условия отправки.
- Не внедрять новые внешние сервисы.

## Plan
1. Обновить `core/reminder.py`: parallel fan-out для `get_reminders()` и semaphore для limiter.
2. Убрать лишнее создание клиента на каждый OpenAI запрос, переиспользовать клиент агента в рамках run.
3. Прогнать py_compile + fallback/idempotency smoke + reminders-only mock dry-run.
4. Синхронизировать sprint/context/doc/Jira lifecycle.

## Checklist (DoD)
- [x] `get_reminders()` выполняет enhancer вызовы параллельно.
- [x] Добавлен bounded concurrency для OpenAI запросов.
- [x] fallback/idempotency поведение сохранено.
- [x] Smoke-checks зеленые.
- [x] Jira и docs синхронизированы.

## Work log
- 2026-02-27: Задача создана (`DTM-35`) и переведена в `В работе`, стартовый evidence comment добавлен.
- 2026-02-27: Реализован parallel fan-out enhancer path в `Reminder.get_reminders()` через `asyncio.gather(...)` с `return_exceptions=True`.
- 2026-02-27: Добавлен bounded concurrency (`enhance_concurrency`, semaphore) для OpenAI enhancer path.
- 2026-02-27: `AsyncOpenAIChatAgent` переведен на переиспользуемый `httpx.AsyncClient`/`AsyncOpenAI` вместо создания клиента на каждый запрос.
- 2026-02-27: Добавлен deterministic smoke `agent/reminder_parallel_enhancer_smoke.py` (`max_active>=2`) и пройдены fallback/idempotency/runtime smoke-checks.

## Links
- Jira: DTM-35
- Code: core/reminder.py

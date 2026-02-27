# DTM-34: TSK-037 Stage 4 reminder pipeline decomposition (facts/draft/enhancer/sender)

## Context
- Текущий `Reminder` в `core/reminder.py` совмещает несколько ответственностей в одном классе/методах.
- Stage 4 требует явной декомпозиции reminder-пайплайна без изменения бизнес-поведения.
- DTM-32 и DTM-33 уже закрыли fallback и in-run idempotency; их гарантии должны сохраниться.

## Goal
- Разделить pipeline на явные шаги внутри `Reminder`: подготовка контекста, генерация черновика, enhancer fallback, подготовка доставки.
- Сохранить совместимость текущих entrypoint (`get_reminders`, `send_reminders`) и существующих smoke-проверок.

## Non-goals
- Не менять текстовые шаблоны сообщений и продуктовые правила напоминаний.
- Не добавлять новые внешние интеграции или режимы запуска.

## Plan
1. Вынести шаги pipeline в отдельные приватные helper-методы с явными контрактами.
2. Перевести `get_reminders`/`send_reminders` на новые шаги без изменения результата.
3. Прогнать py_compile + reminder smoke (fallback/idempotency + reminders-only dry-run mock).
4. Обновить sprint/doc/context/Jira evidence.

## Checklist (DoD)
- [x] Pipeline-шаги декомпозированы на отдельные helper-методы.
- [x] Fallback и idempotency поведение сохранены.
- [x] Smoke-проверки прошли успешно.
- [x] Документация и sprint-состояние синхронизированы.
- [x] Jira обновлена комментариями и статусом.

## Work log
- 2026-02-27: Задача создана в Jira (`DTM-34`) и переведена в `В работе`; стартовый evidence comment добавлен.
- 2026-02-27: Декомпозирован reminder pipeline в `core/reminder.py` (context/designers/message build + delivery resolution helpers) без изменения public entrypoint.
- 2026-02-27: Smoke-check пройден: `py_compile`, `agent/reminder_fallback_smoke.py`, `agent/reminder_idempotency_smoke.py`, `local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- Jira: DTM-34
- Code: core/reminder.py

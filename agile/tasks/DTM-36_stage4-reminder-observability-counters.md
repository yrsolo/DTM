# DTM-36: TSK-039 Stage 4 reminder observability counters for send outcomes

## Context
- Reminder flow логирует отдельные события (`mock_telegram_send`, `duplicate_reminder_skip`), но не публикует структурный итог по исходам доставки.
- `GoogleSheetPlanner.build_quality_report()` пока не включает delivery outcome counters для reminder ветки.

## Goal
- Добавить в reminder structured counters исходов отправки.
- Пробросить counters в `quality_report` без изменения продуктового поведения reminder flow.

## Non-goals
- Не менять текст сообщений, логику fallback/idempotency и run-mode правила.
- Не менять интеграции с Telegram/OpenAI.

## Plan
1. Добавить counters lifecycle в `core/reminder.py` (reset/inc/export + summary print).
2. Подключить counters в `core/planner.py` quality report.
3. Добавить/обновить smoke для проверки counters и прогнать reminders-only dry-run mock.
4. Обновить sprint/context/doc + Jira lifecycle.

## Checklist (DoD)
- [x] Reminder counters покрывают ключевые исходы send path.
- [x] `quality_report` включает reminder counters.
- [x] Smoke-checks зеленые.
- [x] Sprint/docs/Jira синхронизированы.

## Work log
- 2026-02-27: Создана Jira задача `DTM-36`, переведена в `В работе`, добавлен start evidence.
- 2026-02-27: Добавлены structured delivery counters в `Reminder.send_reminders()` (sent/skipped/error classes) + summary print.
- 2026-02-27: `GoogleSheetPlanner.build_quality_report()` расширен `reminder_delivery_counters` + summary fields `reminder_sent_count`, `reminder_send_error_count`.
- 2026-02-27: Добавлен smoke `agent/reminder_delivery_counters_smoke.py`; также пройдены fallback/idempotency/parallel smoke и reminders-only mock dry-run.

## Links
- Jira: DTM-36
- Code: core/reminder.py, core/planner.py

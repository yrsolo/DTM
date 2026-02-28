# DTM-37: TSK-040 Stage 5 kickoff derived SLI counters for reminder delivery/failure rates

## Context
- DTM-36 добавил raw delivery counters reminder path.
- В quality report пока нет derived SLI-метрик (attemptable denominator, success/failure rates).
- Stage 5 требует эксплуатационные SLI/SLO, начиная с reminder delivery.

## Goal
- Вычислять и публиковать derived reminder SLI в `quality_report`.
- Зафиксировать формулу и smoke-проверку вычисления метрик.

## Non-goals
- Не менять send-поведение, режимы запуска и интеграции.
- Не вводить внешний storage/историю метрик на этом шаге.

## Plan
1. Добавить функцию расчета reminder SLI summary в `core/planner.py`.
2. Подключить derived поля в `build_quality_report()` и `main` summary print.
3. Добавить smoke script для deterministic валидации формулы.
4. Обновить sprint/context/doc/Jira.

## Checklist (DoD)
- [x] Derived SLI поля добавлены в quality report summary.
- [x] Формула attemptable/delivery/failure rate зафиксирована кодом.
- [x] Smoke-checks зеленые.
- [x] Sprint/docs/Jira синхронизированы.

## Work log
- 2026-02-27: Создана Jira задача `DTM-37`, переведена в `В работе`, добавлен start evidence.
- 2026-02-27: Добавлен расчетчик `build_reminder_sli_summary(...)` в `core/planner.py` с полями `reminder_delivery_attemptable_count`, `reminder_delivery_attempted_count`, `reminder_delivery_rate`, `reminder_failure_rate`.
- 2026-02-27: `build_quality_report()` и `main` summary расширены derived SLI полями.
- 2026-02-27: Добавлен deterministic smoke `agent/reminder_sli_summary_smoke.py`; пройдены compile + reminder smoke + reminders-only mock dry-run.

## Links
- Jira: DTM-37
- Code: core/planner.py, main.py

# DTM-38: TSK-041 Stage 5 kickoff risk-register update for reminder/API degradation and retry policy

## Context
- `doc/05_risk_register.md` содержит устаревшие mitigation формулировки по reminder/API рискам.
- После Stage 4/5 реализованы fallback, idempotency guard, bounded parallel enhancer, delivery counters и derived SLI summary.
- Нужна актуализация risk-register и явная позиция по retry policy.

## Goal
- Обновить risk-register по reminder/OpenAI/Telegram/Google API рискам в соответствии с текущим runtime.
- Зафиксировать текущую retry-policy позицию (что реализовано сейчас, что в backlog).

## Non-goals
- Не менять runtime-код и внешние интеграции.
- Не вводить новый механизм retries в этом шаге.

## Plan
1. Сопоставить текущие риски `R-003/R-005/R-006` с фактическими mitigation в коде/доках.
2. Обновить `doc/05_risk_register.md` (mitigation/status/notes).
3. Синхронизировать sprint/context/backlog записи и Jira evidence.
4. Прогнать smoke sanity-check для reminders-only dry-run mock.

## Checklist (DoD)
- [x] Risk-register обновлен и согласован с текущим runtime.
- [x] Retry-policy позиция зафиксирована явно.
- [x] Smoke sanity-check выполнен.
- [x] Sprint/docs/Jira синхронизированы.

## Work log
- 2026-02-27: Jira `DTM-38` создана и переведена в `В работе`, добавлен start evidence.
- 2026-02-27: `doc/05_risk_register.md` обновлен по Stage 4/5 фактам: idempotency/fallback/parallel/counters/derived SLI, добавлены актуальные статусы и notes.
- 2026-02-27: Зафиксирована explicit retry-policy stance: для Google/Telegram retries остаются pending risk-ownership item (no full retry/backoff implementation yet).
- 2026-02-27: Smoke sanity-check выполнен: `local_run.py --mode reminders-only --dry-run --mock-external` прошел успешно.

## Links
- Jira: DTM-38
- Docs: doc/05_risk_register.md

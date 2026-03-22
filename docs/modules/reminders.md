# `reminders`

## Роль

`reminders` владеет reminder-сценарием:
- выбором кандидатов;
- сборкой reminder payload;
- enrichment/styling;
- delivery orchestration;
- retry/accounting логикой reminder execution.

## Главные входы

- queue-backed `send_reminders`;
- planner/runtime execution path для scheduled reminder runs.

## Что модуль не должен делать

- превращаться в trigger shell;
- зависеть от deep Telegram internals;
- размазывать reminder semantics по `platform` и transport code.

## Finish line

Напоминание считается выполненным, когда модуль принял решение, собрал payload и довёл delivery через свой канонический execution surface.

# Документация DTM

В `docs/` лежит системная и продуктовая документация проекта. Это не execution-tracking: рабочие планы, кампании и текущее состояние живут в `work/`.

## Start here

- [product/README.md](product/README.md) — быстрый вход: что это за система и какие задачи она решает
- [architecture/README.md](architecture/README.md) — как устроен текущий runtime
- [operations/README.md](operations/README.md) — как это запускать, проверять и сопровождать
- [reference/README.md](reference/README.md) — сухие контракты, режимы, конфиги и схемы

## Deep dives

- [architecture/runtime/architecture.md](architecture/runtime/architecture.md)
- [integrations/attachments/backend-flow.md](integrations/attachments/backend-flow.md)
- [integrations/browser-auth/contract.md](integrations/browser-auth/contract.md)
- [operations/runbook.md](operations/runbook.md)
- [reference/contracts.md](reference/contracts.md)

## Когда использовать этот раздел

Используй `docs/`, когда нужно:

- быстро понять, что такое DTM и где искать нужную тему
- разобраться в текущем устройстве runtime и внешних контурах
- найти рабочий runbook или технический контракт
- перейти из обзорного уровня в глубокий документ по ссылкам

## Структура

- [product/README.md](product/README.md) — лёгкий верхний слой про продукт и возможности
- [architecture/README.md](architecture/README.md) — устройство системы, runtime и snapshot engine
- [integrations/README.md](integrations/README.md) — browser auth, attachments, Telegram и внешние контуры
- [operations/README.md](operations/README.md) — runbook, observability, infra
- [reference/README.md](reference/README.md) — конфиг, контракты, режимы, схемы статусов
- [archive/README.md](archive/README.md) — исторические и superseded материалы

## Process boundary

Процессы, кампании, backlog и текущее execution state находятся в [../work/README.md](../work/README.md).

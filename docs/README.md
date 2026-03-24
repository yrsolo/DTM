# Карта документации

`docs/` содержит только актуальную документацию текущей системы.  
Process, tracking и кампании живут в `work/`. История и superseded материалы живут в `archive/`.

## Если знакомишься с проектом

- [product/overview.md](product/overview.md)
- [architecture/overview.md](architecture/overview.md)
- [modules/README.md](modules/README.md)
- root [README.md](../README.md) как карта active code map

## Если сопровождаешь живой контур

- [operations/runbook.md](operations/runbook.md)
- [operations/browser-auth.md](operations/browser-auth.md)
- [operations/infrastructure/README.md](operations/infrastructure/README.md)
- [operations/observability/README.md](operations/observability/README.md)

## Если нужен точный reference

- [reference/configuration.md](reference/configuration.md)
- [reference/contracts.md](reference/contracts.md)
- [reference/runtime-modes.md](reference/runtime-modes.md)
- [reference/job-status-schema.md](reference/job-status-schema.md)
- [reference/browser-auth.md](reference/browser-auth.md)

## Разделы

- [product/README.md](product/README.md) — что такое DTM и какие сценарии он покрывает
- [architecture/README.md](architecture/README.md) — текущая архитектура и runtime canon
- [modules/README.md](modules/README.md) — active owning modules и их границы
- [operations/README.md](operations/README.md) — runbook, infra, observability, operator flows
- [reference/README.md](reference/README.md) — конфиг, контракты, режимы и схемы

## Что не лежит в `docs/`

- process и execution tracking — [../work/README.md](../work/README.md)
- agent/development instructions — `AGENTS.md` и `agent/**`
- исторические аудитные и миграционные материалы — [../archive/docs/README.md](../archive/docs/README.md)

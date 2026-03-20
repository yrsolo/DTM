# Designers Task Manager

DTM is a lightweight operations hub for design teams that need one place to keep tasks, people, deadlines, reminders, and file flows in sync without building a heavy bespoke PM stack.

It sits on top of familiar tools, keeps reads fast and predictable, and pushes expensive or risky work into controlled async jobs.

## What DTM gives you

- A browser-safe operational API over prepared task data
- Snapshot-based reads that stay stable under load
- Queue-backed mutations for refresh, renders, reminders, and attachments
- Operator tooling in `/info` for diagnostics and live contour checks
- File attachment flow with upload, finalize, view, download, and delete
- Google Sheets as the practical source system for task operations

## Who it is for

- Design operations teams
- Managers coordinating designers through Sheets-centric workflows
- Engineers supporting internal planning and reminder automations
- Operators who need clear runbooks and observable async flows

## Architecture tags

`snapshot-first` `queue-backed` `google-sheets` `browser-safe-reads` `async-mutations` `object-storage` `serverless`

## Where to go next

- [Документация по проекту](docs/README.md)
- [Быстрый обзор продукта](docs/product/README.md)
- [Архитектура и устройство runtime](docs/architecture/README.md)
- [Active architecture canon](docs/architecture/module-first-recovery/README.md)
- [Интеграции и внешние контуры](docs/integrations/README.md)
- [Эксплуатация и наблюдаемость](docs/operations/README.md)
- [Справочные схемы и контракты](docs/reference/README.md)
- [Текущее execution-tracking пространство](work/README.md)

## Fast reading path

If you want the cleanest first pass through the repo:

1. [docs/product/overview.md](docs/product/overview.md)
2. [docs/architecture/module-first-recovery/README.md](docs/architecture/module-first-recovery/README.md)
3. [docs/integrations/attachments/frontend-card-publication.md](docs/integrations/attachments/frontend-card-publication.md)
4. [index.py](index.py)
5. [src/entrypoint/handler.py](src/entrypoint/handler.py)

## Project posture

DTM deliberately prefers:

- deterministic read paths over live query improvisation
- explicit async jobs over hidden side effects
- small browser-facing contracts over generic passthrough APIs
- operational clarity over cleverness

If you need the historical migration story or legacy investigations, use [docs/archive/README.md](docs/archive/README.md) and [work/archive/README.md](work/archive/README.md).

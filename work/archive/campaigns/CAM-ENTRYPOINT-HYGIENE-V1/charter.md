# CAM-ENTRYPOINT-HYGIENE-V1 — Убрать гиперфункции (простыни параметров) через Context/DTO

## Goal
Убрать “простыни параметров” и заменить их на:
- `AppContext` (deps + cfg + logger + clock)
- DTO (`HttpRequest`, `RunRequest`)
- Классы/объекты для router/job вместо mega-функций

## Problem statement
Агентский рефакторинг часто превращает 100 функций в 3 гиперфункции с десятками аргументов. Это сохраняет грязь, но прячет её.

## Scope
- Вынести аргументы hyperfunctions в контекст и датаклассы.
- Превратить build_*_handlers и run_*_pipeline функции в объекты.

## Deliverables
- `AppContext` как единственный носитель deps/config.
- `HttpRouter(ctx).dispatch(req)`
- `TimerPipeline(ctx).run(run_request)` вместо функций с десятками параметров.
- Удаление передач функций-колбэков как аргументов (safe_print, mapper funcs и т.п.)

## DoD
- Ни один entrypoint / pipeline runtime метод не принимает “простыню” параметров.
- Сигнатуры функций становятся короткими и стабильными.

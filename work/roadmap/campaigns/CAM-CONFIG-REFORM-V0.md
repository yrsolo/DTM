# CAM-CONFIG-REFORM-V0 — ENV минимизировать, остальное в YAML (нулевая кампания)

## Goal
Сделать конфигурацию управляемой и прозрачной:
- в **ENV** оставить только секреты и строго deployment-specific параметры;
- все остальные настройки вынести в **открытые YAML** (репозиторий), разбив по темам;
- во всём коде заменить чтение `os.getenv()` и “констант про всё” на единый `cfg` объект.

## Problem statement
Сейчас пайплайн утопает в:
- сотнях env/констант,
- проверках “если такой флаг — то так”,
- пробрасывании параметров по функциям.

Это мешает:
- читать код,
- тестировать,
- стабильно рефакторить `index.py/main.py`,
- контролировать поведение между dev/prod.

## Scope
Decision baseline (owner, 2026-03-04):
- API v1 support is discontinued; this campaign should treat API v2 as the only maintained API contract.

1) Ввести структуру конфигурационных файлов:
   - `config/runtime.yaml` — интервалы, TTL, включатели “feature-ish” (не секретные)
   - `config/tables.yaml` — Google Sheets: листы, ranges, колонки, лимиты
   - `config/db.yaml` — YDB: имена таблиц, TTL, readmodel_id, режимы чтения (не секреты)
   - `config/llm.yaml` — провайдер, модели, таймауты, лимиты (без ключей)
   - `config/mapping.yaml` — color→status, enum mapping, milestone types
2) Добавить загрузчик конфигов:
   - `src/config/schema.py` (pydantic/dataclasses)
   - `src/config/loader.py` (load YAML + merge overrides)
3) Ограничить ENV:
   - только секреты (tokens/keys/service account) и deployment-specific (domain, proxy, ENV=dev/prod).
4) Обновить код так, чтобы:
   - entrypoints получают `cfg` из bootstrap,
   - `src/services/*` и `src/core/*` не читают env/const напрямую.

## Non-goals
- Не рефакторить архитектуру модулей (это следующие кампании).
- Не менять бизнес-логику синка/версий/майлстоунов.

## Deliverables
- `config/*.yaml` (5 файлов)
- `src/config/{schema.py,loader.py}`
- `src/app/bootstrap.py` (создаёт cfg и передаёт его дальше)
- Док: `docs/system/config.md` с “что где настраивается” и списком оставшихся ENV.

## Rules (hard)
- Запрет `os.getenv()` вне `src/config/loader.py` и `src/app/bootstrap.py`.
- Запрет `from config.constants import ...` в `src/services/*` и `src/core/*`.
- Все “поведенческие” параметры должны жить в YAML (или иметь YAML default).

## Suggested ENV allowlist (пример)
Оставить в ENV:
- `ENV` (dev/prod)
- `YC_SA_JSON_CREDENTIALS` / путь к ключу / metadata mode (секрет)
- `TELEGRAM_TOKEN` (секрет)
- `OPENAI_API_KEY` / ключи провайдеров LLM (секрет)
- `PROXY_URL` (deployment-specific)
- `PUBLIC_BASE_URL` / домен (deployment-specific)

Всё остальное → YAML.

## Phases & tasks
### P01 — Config files + loader
- T001: Создать `config/` и 5 YAML файлов со схемой ключей.
- T002: Создать `src/config/schema.py` (типизированные структуры).
- T003: Создать `src/config/loader.py` (load + validate + env override только allowlist).
- T004: Обновить `docs/system/config.md`.

### P02 — Bootstrap + dependency wiring
- T001: Создать `src/app/bootstrap.py`:
  - `cfg = load_config()`
  - создать клиентов/репозитории/сервисы на базе cfg
- T002: `index.py/main.py` получают cfg только через bootstrap (не читают env напрямую).

### P03 — Removal of constants/env usage in services/core
- T001: Убрать прямые импорты `config/constants.py` из `src/services/*` и `src/core/*`.
- T002: Заменить на `cfg.*` в точках, где нужен параметр.

### P04 — Compatibility bridge (если надо)
- T001: На 1 релиз оставить чтение старых env, но логировать `DEPRECATED_*`.
- T002: После smoke убрать мост.

## DoD
- В runtime pipeline отсутствует чтение env вне bootstrap/loader.
- Количество ENV переменных в проде уменьшается до “секреты + 2–5 deployment-specific”.
- Для запуска dev/prod достаточно менять YAML + секреты в ENV/Lockbox.

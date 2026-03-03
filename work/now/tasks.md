# Active Tasks

- [x] Activate `CAM-CONFIG-REFORM-V0` from priorities.
- [x] P01-T001: create YAML config files (`runtime`, `tables`, `db`, `llm`, `mapping`).
- [x] P01-T002: add typed config schema scaffold (`src/config/schema.py`).
- [x] P01-T003: add config loader scaffold (`src/config/loader.py`) with ENV allowlist.
- [x] P01-T004: refresh `docs/system/config.md` (new config source map + ENV allowlist).
- [x] P01-T005: remove duplicated mapping/table defaults from `config/constants.py`, source them from YAML.
- [x] P01-T006: move `HELPER_CHARACTER` and `TRIGGERS` to YAML + remove YAML-covered defaults from all `.env*`.
- [x] P01-T007: move web/storage/deploy defaults to YAML and simplify deploy/release GitHub workflows.
- [x] P01-T008: reduce `.env` and `.env.example` to secrets/overrides only; remove baked non-secret constants.
- [x] Owner review gate: confirm YAML transfer scope before first commit.
- [x] P01-T009: remove legacy `TARGET_SHEET_NAME_PROD` requirement from runtime/release contour.
- [x] P02-T001: start bootstrap wiring in `index.py/main.py` (in progress).
- [ ] P02-T002: move entrypoint env flags to YAML/config loader (`DEBUG_HTTP_EVENT` done; continue on remaining flags).
- [x] P03-T001: remove direct `os.getenv` usage from adapters in runtime path (`src/adapters/ydb/client.py`, `src/adapters/store_ydb.py`).

## Blockers
- none

## Last Update
- 2026-03-04 (P03-T001 completed; runtime adapters no longer read env directly, moved to centralized constants/config path)

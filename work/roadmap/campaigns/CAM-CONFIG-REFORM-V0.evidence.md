# CAM-CONFIG-REFORM-V0 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `docs/system/config.md`, `docs/system/architecture.md`, `work/roadmap/campaigns/priorities.md` | 2026-03-03 | TeamLead agent | direct read of current docs + priority queue | high | campaign priority and target contour confirmed |
| `config/constants.py`, `index.py`, `main.py`, `src/adapters/ydb/client.py` | 2026-03-03 | TeamLead agent | code scan (`rg`) for env/constants coupling and runtime entrypoints | high | current state has strong env/constants coupling; refactor needed |

## Execution Log
- CAM-CONFIG-REFORM-V0 activated in `work/now/campaign.md`.
- P01 task list initialized in `work/now/tasks.md`.
- Owner rule acknowledged: no commits before YAML transfer scope review.
- P01 scaffold implemented (uncommitted):
  - YAML config files added: `config/runtime.yaml`, `config/tables.yaml`, `config/db.yaml`, `config/llm.yaml`, `config/mapping.yaml`
  - typed schema scaffold: `src/config/schema.py`
  - loader scaffold + env allowlist: `src/config/loader.py`
  - bootstrap scaffold: `src/app/bootstrap.py`
  - docs update: `docs/system/config.md`
  - dependency note: `PyYAML` added to `requirements.txt`
  - constants dedup: `config/constants.py` now sources sheet names/field maps/color maps/hidden stages and runtime defaults from YAML loader (`load_config()`), without hardcoded duplicates.
  - constants transfer: `HELPER_CHARACTER` moved to `config/llm.yaml` (`assistant.helper_character`), `TRIGGERS` moved to `config/runtime.yaml` (`triggers`).
  - env cleanup: removed YAML-covered defaults from `.env`, `.env.example`, `.env.dev.example`, `.env.prod.example` (runtime/sheet/source/pipeline/source-select keys).
  - added deploy defaults map: `config/deploy.yaml` (folder/function/runtime/timeout/entrypoint/service-account id).
  - moved web defaults to `config/runtime.yaml` and object storage defaults to `config/db.yaml`.
  - updated workflows to consume YAML defaults instead of repo vars/secrets for non-sensitive deploy settings:
    - `.github/workflows/deploy_yc_function_main.yml`
    - `.github/workflows/release_yc_function_prod.yml`
  - `.env` cleaned to secrets/override-only keys; non-secret constants removed.
  - `.env.example` rewritten to minimal secret/override template; `.env.dev.example` and `.env.prod.example` reduced to optional override stubs.
- Local smoke check:
  - `.venv\\Scripts\\python.exe -c "from src.config.loader import load_config; cfg=load_config(); print('ok', bool(cfg.tables.sheet_names), bool(cfg.mapping.project_aliases), cfg.db.tables.get('tasks'))"`
  - result: `ok True True dtm_tasks`
  - `.venv\\Scripts\\python.exe -c "from src.config.loader import load_config; cfg=load_config(); import config.constants as c; print('cfg', bool(cfg.tables.sheet_names), bool(cfg.mapping.project_aliases)); print('const', len(c.SHEET_NAMES), len(c.TASK_FIELD_MAP), len(c.PEOPLE_FIELD_MAP), len(c.REPLACE_NAMES), len(c.COLOR_STATUS), len(c.NO_VISIBLE_STAGES))"`
  - result: `cfg True True` and `const 7 11 8 26 5 6`

# Config Import Migration Checklist (CAM-CONFIG-REFORM-V0)

## Audit snapshot (2026-03-04)

Remaining direct config imports in active contour:
- `index.py` -> `from config import (...)`
- `main.py` -> `from config import (...)`
- `src/app/planner_bootstrap.py` -> `from config import (...)`
- `core/timing_parser.py` -> `from config import TIMING_YEAR_MODE`
- `core/reminder.py` -> `from config import DEFAULT_CHAT_ID, TG`
- `src/services/calendar_runtime.py` -> `from config import COLORS`
- `src/adapters/telegram.py` -> `from config import DEFAULT_CHAT_ID, TG`
- `src/adapters/google_sheets/task_repository.py` -> `from config import COLOR_STATUS, REPLACE_NAMES, TASK_FIELD_MAP`
- `src/adapters/google_sheets/people_manager.py` -> `from config import PEOPLE_FIELD_MAP`
- `src/adapters/store_ydb.py` -> `from config.constants import YC_SA_JSON_CREDENTIALS, YC_SA_KEY_FILE`
- `src/adapters/ydb/client.py` -> `from config.constants import (...)`

Additional agent-only imports:
- `agent/backfill_milestones_versions.py`
- `agent/migrate_milestones_to_v.py`

## Migration order (safe path)
1. `src/app/planner_bootstrap.py`: introduce cfg-driven settings input and move non-secret defaults from global config imports to `cfg`.
2. `main.py` and `index.py`: read runtime values from `build_app_context().cfg` and pass them into bootstrap/runtime calls.
3. `src/services/calendar_runtime.py` and Google Sheets adapters: consume mappings/colors/field maps from injected cfg instead of module globals.
4. `core/timing_parser.py`: pass `timing_year_mode` from caller cfg/bootstrap; remove module-level default from `config`.
5. Keep secret-only env/constants in adapters until dedicated secret provider abstraction is added.

## Guardrails
- No behavior changes in same patch as config source swap.
- Keep compatibility defaults for one migration step, then remove after smoke pass.
- Every swap must be covered by:
  - `python -m py_compile ...`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty -v`

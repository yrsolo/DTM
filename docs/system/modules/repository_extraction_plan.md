# Repository Extraction Plan (Core Cleanup)

## Goal
Move IO-heavy Google Sheets repository logic out of `core/repository.py` while keeping runtime behavior unchanged.

## Current mixed areas in `core/repository.py`
- Domain pieces:
  - `Task` model
  - `TaskRepository` interface
  - timing/year-shift diagnostics around parsed milestones
- Infra pieces:
  - `GoogleSheetsTaskRepository` implementation
  - direct `GoogleSheetsService` usage
  - worksheet/color reads and assistant-sheet reads

## Atomic extraction sequence
1. Create adapter module `src/adapters/google_sheets/task_repository.py` and copy `GoogleSheetsTaskRepository` there.
2. Keep compatibility shim in `core/repository.py`:
   - re-export `GoogleSheetsTaskRepository` from adapter module.
3. Move sheet-read helpers (`_load_and_process_data`, `_validate_required_columns`) into adapter module unchanged.
4. Keep `Task` and `TaskRepository` in `core/repository.py` until consumers are fully switched.
5. After import switch is stable, split `Task` into `core/models/task.py` and leave a shim.

## Safety checks per step
- `python -m py_compile core/repository.py src/adapters/google_sheets/task_repository.py`
- run existing smoke: `python -m unittest tests.services.test_pipeline_runtime -v`
- verify no new `os.getenv` in moved adapter module.


# System docs

## Contents
- `architecture.md` — high-level architecture and boundaries
- `dataflow.md` — canonical pipeline (Sheets → hash gate → normalize → version → YDB → readmodel)
- `ydb_schema.md` — YDB tables and their meaning
- `runtime_modes.md` — intended runtime modes
- `entrypoints_index_main.md` — what `index.py` and `main.py` do today
- `module_map.md` — module inventory (what exists and where)
- `core_boundaries.md` — `core/` inventory and domain/infra split status
- `config.md` — env/config overview (current state)
- `runbook.md` — minimal operations guide

## Module notes
`docs/system/modules/` can contain module-level notes as the codebase is refactored.

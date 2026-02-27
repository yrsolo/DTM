# DTM-58: TSK-061 Stage 6 slice: publication path for read-model artifacts without runtime impact

## Context
- Stage 6 read-model contract and builder are already implemented.
- Local launcher currently writes quality/alert artifacts but has no read-model output option.
- Need an explicit optional publication path that does not alter existing runtime behavior when flag is absent.

## Goal
- Add local launcher option to emit read-model artifact file from current run outputs.
- Keep existing modes and side-effect behavior unchanged by default.

## Non-goals
- No API service publishing.
- No UI implementation.
- No production deployment changes.

## Plan
1. Verify freshness for local launcher + read-model builder integration points.
2. Add `local_run.py` read-model artifact options and wiring.
3. Add deterministic smoke for artifact publication path.
4. Sync sprint/context/backlog/docs and Jira lifecycle.

## Checklist (DoD)
- [x] `local_run.py` supports optional read-model artifact output.
- [x] Publication path smoke confirms valid artifact shape.
- [x] Sprint/context/backlog/task docs synchronized.
- [x] Jira lifecycle complete (`Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ` -> evidence -> `Ð“Ð¾Ñ‚Ð¾Ð²Ð¾`).

## Work log
- 2026-02-27: Jira `DTM-58` created and moved to `Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ`; start evidence comment posted.
- 2026-02-27: Sprint/task synchronization started for read-model publication slice.
- 2026-02-27: Added local launcher options `--read-model-file` and `--read-model-build-id` with builder wiring through `core.read_model.build_read_model`.
- 2026-02-27: Added deterministic smoke `agent/read_model_publication_smoke.py`.
- 2026-02-27: Smoke checks passed (`.venv\Scripts\python.exe -m py_compile core\read_model.py local_run.py agent\read_model_builder_smoke.py agent\read_model_publication_smoke.py`, `.venv\Scripts\python.exe agent\read_model_publication_smoke.py`, `.venv\Scripts\python.exe local_run.py --help`).
- 2026-02-27: Completion Telegram update sent to owner with Stage 6 tracker state (`done 4`, `remaining 4`).

## Links
- Jira: DTM-58
- Sources: local_run.py, core/read_model.py, doc/stages/11_stage6_read_model_contract.md, agile/sprint_current.md

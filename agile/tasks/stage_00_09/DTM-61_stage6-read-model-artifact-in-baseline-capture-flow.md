# DTM-61: TSK-064 Stage 6 slice: include read-model artifact in baseline capture flow

## Context
- Stage 6 read-model artifact can be produced in `local_run.py`.
- Baseline helper currently captures `quality_report.json` and `alert_evaluation.json`, but not read-model.

## Goal
- Extend baseline helper to also persist `read_model.json`.
- Keep capture behavior stable and backward-compatible.

## Non-goals
- No API publishing.
- No UI runtime changes.

## Plan
1. Verify integration points in `agent/capture_baseline.py` and docs.
2. Add read-model artifact output wiring.
3. Update baseline docs/checklist.
4. Run smoke checks and sync lifecycle/docs.

## Checklist (DoD)
- [x] Baseline bundle includes `read_model.json`.
- [x] Docs/checklist updated for new artifact.
- [x] Smoke checks pass.
- [x] Jira lifecycle complete.

## Work log
- 2026-02-27: Jira `DTM-61` created and moved to `Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ`; start evidence comment posted.
- 2026-02-27: Extended `agent/capture_baseline.py` to pass `--read-model-file` and `--read-model-build-id` into `local_run.py`.
- 2026-02-27: Updated baseline docs/checklist for `read_model.json` artifact (`README.md`, `doc/ops/baseline_validation_and_artifacts.md`).
- 2026-02-27: Smoke checks passed (`.venv\Scripts\python.exe -m py_compile agent\capture_baseline.py local_run.py core\read_model.py`, `.venv\Scripts\python.exe agent\capture_baseline.py --help`, `.venv\Scripts\python.exe agent\read_model_publication_smoke.py`).
- 2026-02-27: Completion Telegram update sent to owner with Stage 6 tracker state (`done 7`, `remaining 1`).

## Links
- Jira: DTM-61
- Sources: agent/capture_baseline.py, local_run.py, doc/ops/baseline_validation_and_artifacts.md

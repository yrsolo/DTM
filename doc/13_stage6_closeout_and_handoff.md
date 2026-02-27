# Stage 6 Closeout And Handoff

## Stage 6 Readiness Gate
Stage 6 is considered complete only if all checks are true:
- Read-model contract exists and is versioned (`doc/11_stage6_read_model_contract.md`).
- Builder implementation exists (`core/read_model.py`).
- Compatibility guard exists (`validate_read_model_contract` + smoke).
- Local publication path exists (`local_run.py --read-model-file`).
- Baseline capture flow includes `read_model.json` (`agent/capture_baseline.py` + doc/02).
- UI baseline view-spec is documented (`doc/12_stage6_ui_view_spec.md`).
- Sprint/Jira/Context docs are synchronized.

## Delivered Artifacts
- Contract: `doc/11_stage6_read_model_contract.md`
- UI view-spec: `doc/12_stage6_ui_view_spec.md`
- Builder: `core/read_model.py`
- Publication smoke: `agent/read_model_publication_smoke.py`
- Compatibility smoke: `agent/read_model_contract_compat_smoke.py`
- Builder smoke: `agent/read_model_builder_smoke.py`

## Handoff Checklist (to next stage)
1. Decide Stage 7 target: API-first or UI-prototype-first.
2. Freeze read-model schema `1.0.x` for initial integration cycle.
3. Define first integration consumer (CLI exporter/API endpoint/UI adapter).
4. Add regression check to routine CI entrypoint if needed.
5. Keep Stage 6 artifacts in baseline bundle for rollback diagnostics.

## Suggested Next Task Order
1. Read-model API exposure (read-only endpoint over artifact/runtime).
2. UI prototype using `doc/12` mapping.
3. Incremental population of `board.timeline`/`board.by_designer`/`task_details`.

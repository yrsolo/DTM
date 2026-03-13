# Evidence - CAM-2026-03-12-DOC-CODE-REALIGN-V1

## Trust gate
- source: owner-provided reference bundle, active system docs, verified runtime code
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `agent/intructions/DTM-test/docs/system/architecture_values.md`
  - `docs/system/architecture.md`
  - `docs/system/module_map.md`
  - active runtime entry code
- trust_level: medium
- notes:
  - baseline doc set still reflects multiple architectural eras
  - imported brief is accepted as editorial direction, not auto-verified fact

## Verified baseline findings
- `docs/system/module_map.md` still treats `planner_runtime_entry.py` as OK/canonical
- active docs do not yet expose a main-doc browser auth contract
- active doc set does not clearly state that `agent/intructions/DTM-test/**` is reference-only
- architecture values are not yet maintained as a canonical normative doc in the main `docs/system/*` tree

## Required evidence during execution
- before/after list of stale claims removed
- code pointers supporting updated claims
- list of reclassified stale docs
- proof that main docs link to canonical architecture values

## 2026-03-12 execution evidence
- stale claims removed:
  - `docs/system/module_map.md` no longer claims `index.py` still builds runtime context at module import
  - `docs/system/module_map.md` now marks `planner_runtime_entry.py` as transitional instead of silently current/canonical
  - `docs/system/entrypoints_index_main.md` now states import-safe main entrypoints and summary-first `/info`
  - `docs/system/metrics_schema.md` now documents `dtm.info.summary.ms` and `dtm.info.detail.ms`
  - `docs/system/grafana_ops_dashboard.md` now describes the compact dashboard layout and summary-first `/info` operator flow
- code pointers:
  - `index.py:47-81` lazily resolves runtime context and dispatcher; no module-level `AppContext` build
  - `src/entrypoints/runtime/planner_runtime_entry.py:116` builds `AppContext` only inside `run_planner_runtime()`
  - `src/entrypoints/http/info_handler.py:620-633` emits `dtm.info.summary.ms`
  - `src/entrypoints/http/info_handler.py:631-637` emits `dtm.info.detail.ms`
  - `src/entrypoints/http/info_handler.py:613-616` and `src/entrypoints/http/templates/info.js:71` confirm explicit detail mode path
  - `src/infra/grafana_specs.py:146-201` and `src/infra/grafana_specs.py:306-360` define compact stat/timeseries layout and info/flush panels
- reclassified active docs:
  - `README.md`
  - `docs/system/architecture.md`
  - `docs/system/module_map.md`
  - `docs/system/entrypoints_index_main.md`
  - `docs/system/metrics_schema.md`
  - `docs/system/grafana_ops_dashboard.md`
  - `work/roadmap/MASTER_EXECUTION_BRIEF_2026-03-12.md`
- canonical-policy cross-links verified in:
  - `README.md`
  - `docs/system/architecture.md`
  - `docs/system/module_map.md`
  - `work/roadmap/MASTER_EXECUTION_BRIEF_2026-03-12.md`

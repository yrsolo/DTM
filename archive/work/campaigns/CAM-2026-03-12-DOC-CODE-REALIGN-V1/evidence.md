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

## 2026-03-14 trust refresh for P02 auth docs consolidation
- source: active auth docs, auth reference handoff, verified runtime code, deploy workflows
- last_verified_at: 2026-03-14
- verified_by: Codex
- evidence:
  - `docs/system/browser_auth_contract.md`
  - `docs/system/auth_trust_boundary.md`
  - `docs/system/config.md`
  - `docs/system/architecture.md`
  - `docs/system/entrypoints_index_main.md`
  - `docs/system/runbook.md`
  - `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md`
  - `src/entrypoints/http/access_context.py`
  - `src/app/bootstrap.py`
  - `config/runtime.yaml`
  - `.github/workflows/deploy_yc_function_main.yml`
  - `.github/workflows/release_yc_function_prod.yml`
- trust_level: high
- notes:
  - trust boundary behavior, trusted headers, masked fallback, and secret bootstrap were verified against active code
  - deploy wiring for `BROWSER_AUTH_PROXY_SECRET` was verified against current test/prod workflows
  - remaining drift is editorial/operator-facing rather than behavioral

## 2026-03-14 pre-edit drift matrix for P02
- canonical code-backed claims already verified:
  - backend trust logic lives in `src/entrypoints/http/access_context.py`
  - `BROWSER_AUTH_PROXY_SECRET` is bootstrapped from env in `src/app/bootstrap.py`
  - trusted header name and fallback policy are configured in `config/runtime.yaml`
  - both test and prod deploy workflows map `BROWSER_AUTH_PROXY_SECRET` from Lockbox into function env
- stale or incomplete main-doc claims to close:
  - auth function/auth contour is not explicitly described as a separate boundary component in main docs
  - callback paths and browser-facing auth routes are not documented together in one canonical operator-facing package
  - deploy/operator verification steps for `test` and `prod` are scattered and incomplete
  - reference bundle `agent/intructions/DTM-test/**` still contains auth function details not fully promoted into `docs/system/*`

## 2026-03-14 post-edit evidence for P02
- canonical auth doc set now consists of:
  - `docs/system/browser_auth_contract.md`
  - `docs/system/auth_trust_boundary.md`
  - `docs/system/browser_auth_runbook.md`
  - `docs/system/config.md`
  - `docs/system/architecture.md`
  - `docs/system/entrypoints_index_main.md`
- stale claims or omissions closed:
  - main docs now describe auth contour/function as an external boundary component rather than an implicit assumption
  - callback paths are documented in main docs for both `test` and `prod`
  - operator-facing Lockbox/env wiring and rollout verification steps are documented in main docs
  - `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md` is now explicitly treated as reference-only input rather than canonical runtime documentation
- static verification evidence:
  - `docs/system/*` now contains one consistent wording set for:
    - trusted header contract
    - `masked` fallback on untrusted ingress
    - `BROWSER_AUTH_PROXY_SECRET` bootstrap and workflow mapping
    - `/ops/auth/*`, `/test/ops/auth/*`, `/ops/auth/callback`, `/test/ops/auth/callback`
- intentionally left as reference/archive:
  - `agent/intructions/DTM-test/**` remains a historical handoff bundle and not a living main-doc root

## 2026-03-14 trust refresh for P03 current-doc cleanup
- source: current main docs, snapshot-engine docs, verified runtime imports/usages, archive tree
- last_verified_at: 2026-03-14
- verified_by: Codex
- evidence:
  - `README.md`
  - `docs/README.md`
  - `docs/system/architecture.md`
  - `docs/system/module_map.md`
  - `docs/system/contracts.md`
  - `docs/system/entrypoints_index_main.md`
  - `docs/system/runbook.md`
  - `docs/system/runtime_modes.md`
  - `docs/snapshot_engine/README.md`
  - `docs/snapshot_engine/architecture.md`
  - `docs/snapshot_engine/api_v2_parity.md`
  - `docs/snapshot_engine/migration_plan.md`
  - `src/entrypoints/runtime/runtime_shell.py`
  - `src/entrypoints/runtime/local_runtime.py`
  - `src/entrypoints/runtime/planner_runtime_entry.py`
  - `src/entrypoints/http/frontend_v2_handler.py`
  - `src/snapshot_engine/*`
  - `archive/docs/system_legacy/*`
- trust_level: high
- notes:
  - current docs still contain misleading active-looking references to YDB/readmodel/planner-era modules
  - archive tree already contains the correct home for deep legacy detail, so cleanup can be done without losing historical references

## 2026-03-14 pre-edit drift matrix for P03
- misleading current-doc claims observed:
  - `docs/system/module_map.md` still marks `src/adapters/ydb/*` as canonical persistence boundary and keeps YDB/readmodel services in active service inventory
  - `docs/system/contracts.md` still documents YDB table contracts as part of current contracts
  - `docs/system/architecture.md` and `docs/system/entrypoints_index_main.md` still over-explain planner/transitional runtime in current narrative
  - `docs/snapshot_engine/migration_plan.md` is migration-era material living in current tree
  - `README.md` and `docs/README.md` still point readers into a transitional cleanup story rather than a simple current-runtime story
- intended cleanup:
  - current docs become snapshot-first, queue-backed, browser-safe, serverless runtime docs only
  - legacy detail stays only as archive pointer

## 2026-03-14 post-edit evidence for P03
- current docs rewritten:
  - `README.md`
  - `docs/README.md`
  - `docs/system/module_map.md`
  - `docs/system/contracts.md`
  - `docs/system/architecture.md`
  - `docs/system/entrypoints_index_main.md`
  - `docs/system/runbook.md`
  - `docs/system/command_runtime_architecture.md`
  - `docs/system/config.md`
  - `docs/snapshot_engine/README.md`
  - `docs/snapshot_engine/api_v2_parity.md`
- moved to archive:
  - `docs/snapshot_engine/migration_plan.md` -> `archive/docs/system_legacy/snapshot_engine_migration_plan.md`
- misleading current-story claims removed:
  - YDB/readmodel tables are no longer described as current contracts
  - YDB adapters/repositories are no longer presented as active canonical module boundaries
  - planner-era runtime is no longer described as the active architecture center
  - current README/docs start points now lead directly into the snapshot-first runtime story
- static verification result:
  - remaining `YDB`/`planner`/`readmodel`/`legacy` mentions in current docs are limited to:
    - archive pointers
    - anti-goals / historical notes
    - explicit backward-compatibility notes that still exist in live config/metrics policy
- intentionally retained in current docs:
  - `architecture_values.md` keeps transitional/boundary language because it is still normative policy
  - skeleton docs keep anti-goal references where they explicitly constrain future design

## 2026-03-14 trust refresh for P04 attachment docs verification
- source: active attachment upload code, current docs surface, queue/job tests
- last_verified_at: 2026-03-14
- verified_by: Codex
- evidence:
  - `src/entrypoints/http/admin_queue_handler.py`
  - `src/jobs/attach_task_file_job.py`
  - `src/snapshot_engine/engine.py`
  - `src/snapshot_engine/frontend_v2_payload_builder.py`
  - `tests/api/test_command_queue_foundation.py`
  - `tests/jobs/test_attach_task_file_job.py`
  - `tests/snapshot_engine/test_engine_attach_metadata.py`
  - `tests/snapshot_engine/test_query_engine.py`
  - `docs/system/file_attachments_skeleton.md`
  - `docs/system/dataflow.md`
  - `docs/system/entrypoints_index_main.md`
  - `docs/system/command_runtime_architecture.md`
  - `docs/system/contracts.md`
  - `docs/system/README.md`
- trust_level: high
- notes:
  - current runtime already implements presigned upload contract plus queued metadata attach
  - current doc surface still described file attachments as a future skeleton, which was misleading

## 2026-03-14 post-edit evidence for P04
- stale claim removed:
  - `docs/system/file_attachments_skeleton.md` no longer presents attachment upload as future-only work
- current runtime facts documented:
  - `POST /admin/attachments/request-upload` returns the active presigned upload contract
  - `POST /admin/commands/attach-task-file` enqueues `attach_task_file`
  - worker/job path persists metadata into extra snapshot and rebuilds prep
  - API v2 exposes `tasks[].attachments` metadata without object keys
- current surface changes:
  - added `docs/system/file_attachments.md`
  - removed `file_attachments_skeleton.md` from current/future-skeleton map
  - updated `dataflow.md`, `entrypoints_index_main.md`, `command_runtime_architecture.md`, and `contracts.md`


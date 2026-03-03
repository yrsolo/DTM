# Atomic Migration Tasks

Format per task:
- Description
- Files/Modules
- Done
- Verification
- Dependencies
- Risks

## M1: Extract Core Normalize

### M1-T1: Introduce core model contracts
- Description: add canonical dataclasses for raw/normalized entities.
- Files/Modules: `src/core/models/contracts.py`
- Done: dataclasses created with docstrings and typing.
- Verification: `python -m compileall src/core/models/contracts.py`
- Dependencies: none
- Risks: temporary model duplication.

### M1-T2: Normalize interfaces and boundaries
- Description: define `normalize_task`, `parse_stages`, `infer_date` interfaces.
- Files/Modules: `src/core/normalize/interface.py`, `src/core/normalize/*.py`
- Done: interfaces callable and isolated from IO.
- Verification: import smoke in a local script.
- Dependencies: M1-T1
- Risks: mismatch with current legacy expectations.

### M1-T3: Add baseline normalize fixtures
- Description: prepare fixture examples for stages/date inference.
- Files/Modules: `artifacts/fixtures/normalize/*.json` (or existing fixture folder)
- Done: fixtures committed with edge cases (`dd.mm`, malformed stage text).
- Verification: fixture loader smoke.
- Dependencies: M1-T2
- Risks: fixture may not cover all production variants.

### M1-T4: Unit test scaffold for normalization
- Description: add unit tests for core normalize functions.
- Files/Modules: `tests/core/normalize/*`
- Done: at least 1 test per critical function.
- Verification: project test command.
- Dependencies: M1-T2
- Risks: test harness differences in current repo.

## M2: Split Sync vs Render

### M2-T1: Create service skeletons
- Description: add sync/readmodels/notify/render service modules.
- Files/Modules: `src/services/*`
- Done: modules with class/function stubs and clear responsibilities.
- Verification: compile/import smoke.
- Dependencies: M1
- Risks: naming drift with legacy modules.

### M2-T2: Add handler skeletons
- Description: add dedicated handler files for sync/render/notify/readmodels/api.
- Files/Modules: `src/handlers/*`
- Done: handler signatures defined, no breaking integration.
- Verification: compile/import smoke.
- Dependencies: M2-T1
- Risks: confusion between old and new entrypoints.

### M2-T3: Wire non-invasive feature flags
- Description: add config flag placeholders for new path enablement.
- Files/Modules: `config/constants.py` or dedicated config module.
- Done: flags documented, default to legacy-safe behavior.
- Verification: local run still unchanged by default.
- Dependencies: M2-T1
- Risks: accidental activation in prod.

### M2-T4: Parity smoke script
- Description: script that compares old vs new normalize output for sample input.
- Files/Modules: `agent/*` smoke helper.
- Done: script produces diff summary.
- Verification: run script locally.
- Dependencies: M1, M2-T1
- Risks: false positives from ordering differences.

## M3: Source Hash Gate

### M3-T1: Define hash basis contract
- Description: specify which source fields/ranges participate in hash.
- Files/Modules: `docs/contracts/data-contracts.md`, `src/services/sync/hash_gate.py`
- Done: hash basis explicitly documented and implemented.
- Verification: deterministic hash for same input.
- Dependencies: M1
- Risks: omitted fields causing stale sync.

### M3-T2: Implement hash state storage
- Description: add state read/write for last source hash.
- Files/Modules: `src/services/sync/hash_gate.py`
- Done: file/object-store compatible state manager.
- Verification: roundtrip test (`load` -> `save` -> `load`).
- Dependencies: M3-T1
- Risks: corrupted state file handling.

### M3-T3: Add sync skip logic
- Description: integrate hash gate in sync service.
- Files/Modules: `src/services/sync/sync_service.py`
- Done: unchanged source skips heavy sync path.
- Verification: two sequential runs; second marked skipped.
- Dependencies: M3-T2, M2
- Risks: missed update due to hash mismatch bug.

### M3-T4: Add observability fields for skip/run
- Description: add structured log fields for hash_gate decisions.
- Files/Modules: sync service logging path.
- Done: log includes `source_hash`, `previous_hash`, `sync_skipped`.
- Verification: inspect run logs.
- Dependencies: M3-T3
- Risks: noisy logs without clear correlation ids.

## M4: Operational Store (Minimal)

### M4-T1: Store adapter interface
- Description: define repository-style interface for upsert/get/list.
- Files/Modules: `src/adapters/store_ydb.py`, `src/services/sync/sync_service.py`
- Done: service depends on interface, not concrete implementation.
- Verification: compile/import smoke.
- Dependencies: M3
- Risks: mismatch with future YDB schema.

### M4-T2: Minimal upsert implementation
- Description: add minimal implementation (JSON-backed or YDB-backed) for normalized entities.
- Files/Modules: `src/adapters/store_ydb.py` (and local fallback module if needed)
- Done: upsert by `task_id` and stage composite key works.
- Verification: integration smoke with sample payload.
- Dependencies: M4-T1
- Risks: race conditions if concurrent writers appear later.

### M4-T3: Dual-write feature flag
- Description: keep old path while optionally writing to new store.
- Files/Modules: config module + sync service.
- Done: flag OFF by default, ON enables store write.
- Verification: local runs with flag off/on.
- Dependencies: M4-T2
- Risks: hidden partial writes on failures.

### M4-T4: Upsert idempotency smoke
- Description: prove same payload written twice gives stable final state.
- Files/Modules: smoke script + fixture.
- Done: second write does not duplicate records.
- Verification: run smoke script and compare object count.
- Dependencies: M4-T2
- Risks: missing unique key in stage entity.

## M5: Read Models / Vitrina

### M5-T1: Read-model schema v1
- Description: define typed schema for `view_by_designer` and `view_by_tasks`.
- Files/Modules: `docs/contracts/data-contracts.md`, `src/services/readmodels/builder.py`
- Done: schema and examples committed.
- Verification: schema smoke check script.
- Dependencies: M4
- Risks: missing fields needed by renderer/notify.

### M5-T2: Builder implementation (designer/tasks)
- Description: implement deterministic builder from normalized entities.
- Files/Modules: `src/services/readmodels/builder.py`
- Done: returns both views from same input.
- Verification: fixture run and snapshot compare.
- Dependencies: M5-T1
- Risks: ordering instability in output.

### M5-T3: Snapshot tests
- Description: lock expected read-model output on fixtures.
- Files/Modules: `tests/services/readmodels/*`
- Done: snapshots committed, test command green.
- Verification: run tests.
- Dependencies: M5-T2
- Risks: brittle snapshots without useful diff.

### M5-T4: Read-model publication path
- Description: add publish/storage hook for read-model artifact.
- Files/Modules: service/handler + optional object storage helper.
- Done: artifact persisted with build metadata.
- Verification: artifact file/object exists and schema check passes.
- Dependencies: M5-T2
- Risks: stale artifact overwritten without trace.

## M6: Notifications from Read Models

### M6-T1: Notification input switch to read model
- Description: notification service consumes `view_by_designer`.
- Files/Modules: `src/services/notify/notification_service.py`
- Done: old direct-sheet dependency removed from new path.
- Verification: dry-run reminder output matches expectations.
- Dependencies: M5
- Risks: behavior drift on edge formatting.

### M6-T2: Delivery log idempotency key
- Description: persist send keys to avoid duplicate reminders.
- Files/Modules: notify service + storage adapter.
- Done: duplicate sends are skipped by key.
- Verification: repeated run smoke with same inputs.
- Dependencies: M6-T1
- Risks: key design too broad/narrow.

### M6-T3: LLM cache and fallback policy
- Description: cache enhancer outputs and apply fallback per policy.
- Files/Modules: `src/adapters/llm_*`, notify service.
- Done: timeout/error yields deterministic fallback path.
- Verification: provider-offline simulation smoke.
- Dependencies: M6-T1
- Risks: stale cache without expiry strategy.

### M6-T4: Reminder reliability smoke
- Description: add scenario-based smoke for retries and fallback.
- Files/Modules: `agent/*` smoke helper.
- Done: summary reports send success/failure/retry metrics.
- Verification: run smoke script and inspect counters.
- Dependencies: M6-T2, M6-T3
- Risks: mocks diverge from runtime API errors.

## M7: Renderer Optimization

### M7-T1: Renderer layer split (values vs formatting)
- Description: split renderer pipeline into value pass and format pass.
- Files/Modules: render service + google renderer adapter.
- Done: separate methods and timings.
- Verification: render smoke unchanged visual core.
- Dependencies: M5
- Risks: layer order breaks formatting.

### M7-T2: Range diff calculator
- Description: compute minimal changed ranges from old/new read model.
- Files/Modules: render service diff module.
- Done: unchanged cells are skipped.
- Verification: benchmark small payload with few changes.
- Dependencies: M7-T1
- Risks: diff false negatives causing stale cells.

### M7-T3: Batch optimization and metrics
- Description: group update requests and emit batch metrics.
- Files/Modules: renderer adapter + logging.
- Done: reduced API calls and tracked counts.
- Verification: compare call counts before/after.
- Dependencies: M7-T2
- Risks: oversized batch payloads vs API limits.

### M7-T4: Visual parity smoke checklist
- Description: codify visual checks for key sheet zones.
- Files/Modules: `doc/ops/*` checklist.
- Done: manual smoke checklist exists and executed once.
- Verification: checklist evidence in artifact.
- Dependencies: M7-T1
- Risks: manual checks miss subtle style regressions.

## M8: Dashboard API Readiness

### M8-T1: API contract freeze v1
- Description: freeze read-only API response and query contract.
- Files/Modules: `docs/contracts/data-contracts.md`, API contract doc.
- Done: v1 contract tagged and documented.
- Verification: contract smoke script green.
- Dependencies: M5
- Risks: late field additions break compatibility.

### M8-T2: Read-only handlers over read models
- Description: API handlers read from read-model storage only.
- Files/Modules: `src/handlers/api.py` + service wiring.
- Done: no direct source/renderer dependency in API path.
- Verification: endpoint smoke and latency sample.
- Dependencies: M8-T1
- Risks: stale read-model cache.

### M8-T3: API smoke/regression tests
- Description: add endpoint smoke and schema regression checks.
- Files/Modules: `agent/*` smoke + tests.
- Done: payload marker and shape checks in CI/local.
- Verification: run smoke suite.
- Dependencies: M8-T2
- Risks: tests too shallow for real frontend use.

### M8-T4: Frontend integration checklist
- Description: formal handoff checklist for frontend consumer.
- Files/Modules: `doc/ops/*` or `docs/migration/*`.
- Done: checklist includes auth/domain/rate/error expectations.
- Verification: checklist reviewed and signed off.
- Dependencies: M8-T3
- Risks: checklist drifts from deployed runtime.

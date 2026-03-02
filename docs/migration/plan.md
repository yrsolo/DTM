# Migration Plan (M1..M8)

## Migration Constraints
1. No big-bang rewrite.
2. Existing flow must keep working during migration.
3. Every stage ends with explicit entry/exit criteria and rollback plan.
4. All contracts are explicit and versioned in docs/contracts.
5. Rollout policy uses explicit switches:
   - `STORE_MODE=legacy|dual_write|ydb_primary|ydb_only`
   - `READMODEL_SOURCE=legacy|ydb`
   - optional `NOTIFY_SOURCE`, `RENDER_SOURCE` (`legacy|ydb`)

## Stage Matrix

## M1: Extract Core Normalize
- Goal: isolate pure domain models and normalization interfaces.
- Entry: current flow stable, baseline smoke exists.
- Exit: `src/core/models` + `src/core/normalize` introduced, unit tests scaffolded, no runtime behavior change.
- Risks: duplicated logic during transition.
- Rollback: keep new modules unused by default.
- Effort: M

## M2: Split Sync vs Render
- Goal: isolate orchestration into dedicated services/handlers.
- Entry: M1 model/normalize contracts in place.
- Exit: sync and render entrypoints separated in service layer; existing command paths preserved.
- Risks: accidental behavior drift in old flow.
- Rollback: keep old orchestration path behind existing entrypoints.
- Effort: M

## M3: Source Hash Gate
- Goal: skip sync when source range unchanged.
- Entry: source reader boundary identified.
- Exit: hash gate implemented with persisted state; skip path covered by smoke tests.
- Risks: false negatives if hash basis incomplete.
- Rollback: feature flag disables hash gate.
- Effort: S

## M4: Operational Store (Minimal)
- Goal: persist normalized tasks/stages (upsert) into minimal store contour.
- Entry: hash-gated sync stable.
- Exit: normalized entities written to store adapter; idempotent upserts.
- Risks: schema drift and migration friction.
- Rollback: dual-write disabled with env flag.
- Effort: M

## M5: Read Models / Vitrina
- Goal: build explicit read models from store.
- Entry: normalized data in store.
- Exit: `view_by_designer` and `view_by_tasks` generated with snapshot tests.
- Risks: missing fields needed by current renderer.
- Rollback: renderer still consumes old path while parity checked.
- Effort: M

## M6: Notifications from Read Models
- Goal: switch reminders to read-model-based input.
- Entry: stable read models and contracts.
- Exit: notification service reads vitrina; LLM adapter includes cache + fallback + delivery log.
- Risks: changed wording/scheduling edge cases.
- Rollback: fallback to current reminder flow.
- Effort: M

## M7: Renderer Optimization
- Goal: optimize sheet rendering with layers/diff batching.
- Entry: renderer consumes read model.
- Exit: value/format layers split, range diff apply, render metrics tracked.
- Risks: visual regressions in spreadsheet formatting.
- Rollback: full redraw mode feature flag.
- Effort: L

## M8: Dashboard API Readiness
- Goal: read-only API for frontend over read models.
- Entry: read models stable and contract-approved.
- Exit: API endpoints documented + smoke tested + versioned contract.
- Risks: contract churn with frontend coupling.
- Rollback: keep existing API alias and freeze version.
- Effort: M

## Current Progress Marker
- Current repo baseline: pre-M1 implementation with partial API/read-model work already present.
- This package formalizes migration contracts and introduces M1-M3 skeletons for incremental adoption.
- Approved prod rollout order:
  1. `STORE_MODE=dual_write`
  2. switch `READMODEL_SOURCE` / `NOTIFY_SOURCE` to `ydb`
  3. switch store to `ydb_primary`, then `ydb_only`

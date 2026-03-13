# Architecture Agent Addendum — 2026-03-12

Status: active addendum
Applies to: all architecture/refactor/performance/auth work until replaced.

## Mandatory read order for relevant tasks

For tasks touching runtime, read path, auth, metrics, or docs, read in this order:
1. `agent/OPERATING_CONTRACT.md`
2. `AGENTS.md`
3. `docs/system/architecture_values.md`
4. active campaign docs referenced by owner
5. verified code paths

First response requirement remains:
- `CONTRACT CHECK: OK`

## Additional working rules

### 1. Telegram/reminder freeze

Treat Telegram/reminder/group-query as frozen subsystems.

Allowed:
- reading current code to understand dependencies
- minimal break/fix stabilization
- documenting how frozen modules depend on active modules

Forbidden without explicit owner approval:
- major rewrites there before runtime/read/auth cleanup is done
- using frozen modules as architecture exemplars for new subsystems

### 2. Always optimize evidence-first

Do not claim a performance cause without evidence.

For latency/perf tasks, agents must:
- add stage timings first,
- produce before/after evidence,
- separate business execution time from orchestration overhead,
- separate metrics emission time from business time.

### 3. Access control logic belongs at the boundary

For browser-facing auth work:
- auth proxy decides access mode,
- backend creates `AccessContext`,
- read/query code remains canonical,
- masking is a post-build transform.

Forbidden:
- auth branching deep inside query engine
- separate masked query implementation

### 4. Prefer additive refactor seams over big rewrites

When cleaning runtime:
- introduce clear facades and seams,
- move callers gradually,
- delete transitional code only after evidence and parity checks.

### 5. Document drift must be corrected in same campaign

If implementation changes architecture materially, update:
- `docs/system/architecture.md`
- `docs/system/module_map.md`
- `README.md` if public architecture description changed

or record explicitly why each one remains unchanged.

### 6. Required output format for campaigns

Every active campaign should maintain:
- `plan.md`
- `evidence.md`
- optional `notes.md`

Evidence must include:
- verified code paths
- trust level
- before/after metrics or smoke outputs
- unresolved risks

### 7. Safe performance guardrails

When improving speed, do not silently trade away:
- payload contract stability
- masking determinism
- read freshness correctness
- job observability
- security boundaries

### 8. Preferred placement for new modules

- access/auth boundary helpers: `src/entrypoints/http/` or `src/app/`
- masking: `src/services/access/` or `src/app/access/`
- cacheable frontend payload use-cases: `src/services/` or dedicated `src/frontend/` package if introduced deliberately
- performance instrumentation: `src/observability/`

### 9. Explicit anti-goals

Do not create:
- new doc roots,
- new planner-like mega-entrypoints,
- another generic monster context,
- metrics wrappers that hide where network flush really occurs,
- “temporary” random masking hacks.

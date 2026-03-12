# DTM Master Execution Brief — 2026-03-12

Status: active
Audience: implementation agent / team lead agent

## Read this first

Mandatory read order:
1. `agent/OPERATING_CONTRACT.md`
2. `AGENTS.md`
3. `agent/ARCHITECTURE_AGENT_ADDENDUM_2026-03-12.md`
4. `docs/system/architecture_values.md`
5. campaign docs listed below

First response must include:
- `CONTRACT CHECK: OK`

---

## Owner decisions already made

1. Telegram/reminder/group query is frozen for now.
2. Focus first on core/runtime/read/auth/performance/documentation cleanup.
3. Everything described in the architecture audit is accepted in principle.
4. Metrics path must be deeply analyzed because visible refresh is much slower than business refresh.
5. Browser auth must support two modes:
   - full
   - masked
6. Masked mode must preserve payload shape and use deterministic fake dictionaries.

---

## Execution order (strict)

### Stage 1 — P0
`CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1`

Reason:
- current import-time bootstrap and planner-centric top runtime block safe iteration and testability.

### Stage 2 — P0
`CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1`

Reason:
- performance decisions must be evidence-based
- auth/masking should land on top of measured, instrumented read path

### Stage 3 — P1 but can overlap only after stage 1 facts are stable
`CAM-2026-03-12-DOC-CODE-REALIGN-V1`

Reason:
- agents must stop following stale architectural stories

### Stage 4 — P0 after stage 1 and stage 2 foundations exist
`CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1`

Reason:
- auth must land on cleaned runtime and measured frontend path

---

## Non-goals for this wave

Do not spend primary effort on:
- Telegram/reminder redesign
- cosmetic frontend work
- over-generalized framework extraction
- reintroducing planner-centric orchestration under new names

---

## Required implementation style

- small, evidence-backed steps
- additive refactor seams first
- no giant rewrite PRs
- code + docs + evidence updated together
- keep path placement coherent with campaign docs

---

## Required tracking updates

During execution keep updated:
- `work/now/tasks.md`
- `work/roadmap/backlog.md` if scope shifts
- each campaign's `plan.md` and `evidence.md`

If a campaign requires archival/reclassification of old docs, record that explicitly in evidence.

---

## Special notes for auth implementation

Use `BACKEND_AUTH_HANDOFF.md` as browser-facing contract source of truth.

Preferred namespace:
- prod browser API: `/ops/api/...`
- test browser API: `/test/ops/api/...`

Do not continue with older `/prod/api/...` browser contract unless owner explicitly overrides.

---

## Special notes for metrics/performance work

The current top questions are:
1. Why does snapshot refresh show ~5s in metrics but ~20s on info page?
2. How much of hot-path time is spent emitting metrics?
3. Which steps dominate frontend/API latency?
4. Should we prebuild hot cache for common frontend requests?

These questions must be answered with measurements, not guesses.

---

## Final expected outputs from this wave

By the end of this execution wave the repo should have:
- cleaner runtime boundaries
- no import-time production bootstrap in active runtime modules
- measured and optimized metrics path
- lighter/faster info path
- coherent docs aligned to code
- browser auth + masked/full design implemented or at minimum scaffolded with tests and measured hooks

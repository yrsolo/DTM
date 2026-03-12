# MASTER EXECUTION BRIEF - 2026-03-12

Status: active

This is the main-repo execution brief for the 2026-03-12 wave.

Imported source bundle:
- `agent/intructions/DTM-test/**`

Rule:
- imported materials are reference-only input
- execution tracking, campaign state, and evidence live only in main `work/**`

## Read order
1. `agent/OPERATING_CONTRACT.md`
2. `AGENTS.md`
3. `docs/system/architecture_values.md`
4. `docs/system/architecture.md`
5. `docs/system/module_map.md`
6. `docs/system/browser_auth_contract.md`
7. `docs/system/auth_trust_boundary.md`
8. active main campaign docs in `work/roadmap/campaigns/*`
9. verified code paths

## Execution order
1. `CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1`
2. `CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1`
3. `CAM-2026-03-12-DOC-CODE-REALIGN-V1`
4. `CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1`

## Mandatory wave additions
- Stage 1: zero runtime side effects on module import for main entrypoints
- Stage 2: `/info` summary/detail split is mandatory
- Stage 3: architecture values must live in main normative docs
- Stage 4: trusted ingress boundary and untrusted fallback are mandatory

## Freeze and guardrails
- Telegram/reminder/group-query is frozen unless break/fix is required
- performance claims require evidence
- browser auth belongs at the boundary
- imported reference files do not replace main repo policy and docs

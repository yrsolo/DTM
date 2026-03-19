# CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1 Plan

## Rule before decomposition

Before opening any child campaign or implementation wave:
1. read `docs/architecture/runtime/modular-monolith-v2.md`
2. read the relevant ownership docs
3. verify against current code paths
4. update campaign `evidence.md` trust gate
5. only then decompose tasks

## Phases

### P01 - Architectural contract and ownership map
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P01-T001` publish the master modular-monolith document
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P01-T002` publish context, command, route, trigger, bootstrap, and guardrail ownership docs
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P01-T003` publish module-level target docs for the six first-class contexts

### P02 - Target skeleton
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P02-T001` create `src/entrypoint` skeleton
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P02-T002` create `src/platform` skeleton
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P02-T003` create `src/contexts` skeleton for the six first-class contexts

### P03 - Thin handler and mode routing
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P03-T001` extract parsed request/mode classification for the top-level handler
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P03-T002` switch top-level routing to explicit `match/case`
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P03-T003` keep entrypoint transport-only and document any transitional delegations

### P04 - Queue command routing
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P04-T001` normalize command ownership list against current command types
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P04-T002` move worker dispatch to explicit `match/case`
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P04-T003` make runtime/worker transport-only and context-owned for execution

### P05 - Controlled bootstrap transition
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P05-T001` define local context builders and delegation-only bootstrap policy
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P05-T002` prevent new context wiring from accumulating in one global mega-bootstrap

### P06 - Minimal architecture guardrails
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P06-T001` add early import-boundary and entrypoint-thinness gates
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P06-T002` add `os.getenv` and active-path no-legacy-import gates
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P06-T003` add snapshot/rendering boundary gate

### P07 - Trigger orchestration
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P07-T001` move timer orchestration into platform runtime
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P07-T002` move morning orchestration into platform runtime

### P08 - Attachments
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P08-T001` extract `attachments` as the first fully owned context

### P09 - Reminders
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P09-T001` extract `reminders` as a standalone context

### P10 - Snapshot
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P10-T001` extract `snapshot` ownership and public contracts

### P11 - Rendering with enforced boundary
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P11-T001` extract `rendering` ownership
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P11-T002` enforce the hard anti-corruption boundary to `snapshot`

### P12 - Telegram interaction
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P12-T001` extract Telegram webhook and interaction ownership into `telegram_interaction`

### P13 - Access API
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P13-T001` extract browser-facing API ownership into `access_api`

### P14 - Target config centralization
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P14-T001` finish config slicing and target runtime configuration shape

### P15 - Legacy archive and final polish
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P15-T001` archive superseded active-path legacy pieces
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1-P15-T002` finalize docs, guardrails, and contribution guidance


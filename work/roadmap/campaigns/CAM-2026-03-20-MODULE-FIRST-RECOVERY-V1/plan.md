# CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1

## Goal
Replace the architecture-recovery canon with the stricter module-first canon and use a trust-gated delta audit as the first execution wave.

## Status
- in progress: 2026-03-20
- done: 2026-03-20
- current phase: complete

## Phases

### P01 - Freeze the canon
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T001` publish canonical module-first docs under `docs/architecture/module-first-recovery/`
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T002` rewire runtime docs so module-first docs are the primary normative source
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T003` update tracking so `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1` is historical precedent, not current canon
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T004` align module docs with the primary read-model, publication, and reserve-Telegram framing

### P02 - Delta audit against the new canon
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T001` compare current code and docs against the module-first canon
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T002` record what is already true vs still violated
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T003` publish the audit in the structured template format
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T004` define the next code wave from the audit instead of continuing refactor inertia

### P03 - Top path and runtime clarity
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P03-T001` remove or document remaining top-path ambiguity

### P04 - Break bootstrap gravity
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P04-T001` verify bootstrap remains delegation-only and record any remaining gravity points

### P05 - Attachments and publication aftermath
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P05-T001` validate attachment ownership and publication aftermath against the primary read-model scenario

### P06 - Reminders as active module
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P06-T001` validate reminder ownership and delivery flow without Telegram-led redesign

### P07 - Snapshot/rendering hard boundary
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P07-T001` verify snapshot/rendering boundary remains capability-based and readable
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P07-T002` move the snapshot engine physically under the snapshot context

### P08 - Access API around the primary read-model
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P08-T001` validate access-api ownership around the main browser payload

### P09 - Telegram freeze and isolate
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P09-T001` verify Telegram remains isolated and low-maintenance

### P10 - Physical structure cleanup
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P10-T001` remove or demote any remaining folder-level drift against the module-first map
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P10-T002` remove compatibility-only `src/jobs/*` after runtime/context consumers stop importing it

### P11 - Guardrails and done
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P11-T001` align guardrails and final review with the module-first canon

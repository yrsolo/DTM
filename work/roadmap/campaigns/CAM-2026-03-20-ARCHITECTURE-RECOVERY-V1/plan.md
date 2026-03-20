# CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1

## Goal
Replace the modular-monolith V2 canon with the new architecture-recovery canon and use it as the only active architecture roadmap.

## Status
- in progress: 2026-03-20
- current phase: P09 access API as a real module

## Phases

### P01 - Freeze the canon
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T001` publish canonical recovery docs under `docs/architecture/recovery/`
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T002` rewire runtime docs so recovery docs are the primary normative source
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T003` update tracking so the previous modular-monolith umbrella campaign is historical precedent, not current canon

### P02 - Simplify the top path
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P02-T001` reduce competing top-path reading routes and tighten runtime readability guards

### P03 - Break bootstrap gravity
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P03-T001` move remaining domain-specific assembly pressure out of bootstrap and add bootstrap guardrails

### P04 - Attachments as a true first-class module
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P04-T001` move attachment implementation under the context and remove at least one old bridge

### P05 - Decouple cache through intents
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P05-T001` replace direct frontend cache invalidation imports with runtime-owned intents/jobs

### P06 - Reminders as a real module
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P06-T001` move reminder implementation under the context and remove at least one old reminder path

### P07 - Snapshot and rendering split
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P07-T001` replace broad snapshot engine exposure with narrow capabilities and move rendering inward

### P08 - Telegram interaction as a real module
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P08-T001` move telegram implementation inward and separate group-query from reminder internals

### P09 - Access API as a real module
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P09-T001` move access policy and read shaping under the context and thin the HTTP layer

### P10 - Final structure and archive
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P10-T001` archive or demote remaining competing technical clusters

### P11 - Guardrails and done
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P11-T001` finalize review checklist, hard bans, and success closure

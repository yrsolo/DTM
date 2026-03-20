# CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1 Evidence

## Trust gate
- source: current module-first draft, active recovery docs, attachment publication scenario, current code map, module docs
- last_verified_at: 2026-03-20
- verified_by: Codex
- evidence:
  - `agent/intructions/mew_plan2.md`
  - `docs/integrations/attachments/frontend-card-publication.md`
  - `docs/architecture/recovery/README.md`
  - `docs/architecture/runtime/module-map.md`
  - `src/entrypoint/handler.py`
  - `index.py`
- trust_level: high
- notes:
  - the new canon is stricter than the predecessor and changes the active reading priority toward the primary task-list read-model
  - the first code-facing execution wave must be a delta audit against this new canon

## Completed Tasks
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T001`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T002`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T003`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T004`
- [ ] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T001`
- [ ] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T002`
- [ ] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T003`
- [ ] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T004`

## Verification
- Command:
  - `Get-Content agent/intructions/mew_plan2.md`
  - `Get-Content docs/architecture/recovery/README.md`
  - `Get-Content docs/integrations/attachments/frontend-card-publication.md`
  - `Get-Content index.py`
  - `Get-Content src/entrypoint/handler.py`
- Result:
- the new module-first canon introduces a stricter stance than the previous recovery set
- attachment publication and the primary task-list read-model are now explicit governing scenarios
- attachment readiness is treated as an operational signal that leads to task-list refetch, not as the canonical browser read artifact
- Telegram is now treated as reserve capability, not a co-equal active architecture center

## Notes
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1` remains closed as phase-one precedent.
- No new code refactor should start under this campaign before the delta audit is recorded in the structured template format.

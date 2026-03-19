# CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1 Evidence

## Trust gate
- source: active runtime docs, modularity audit, current context/module code, owner-provided recovery plan
- last_verified_at: 2026-03-20
- verified_by: Codex
- evidence:
  - `docs/architecture/runtime/modular-monolith-v2.md`
  - `docs/architecture/runtime/modularity-audit-2026-03-19.md`
  - `src/contexts/*/module.py`
  - `src/contexts/*/public.py`
  - `agent/intructions/new_plan.md`
- trust_level: high
- notes:
  - recovery canon replaces the previous normative source because the audit shows the existing modular-monolith wave stopped at phase-one modularity
  - current runtime docs such as `module-map.md` remain descriptive evidence, not the new normative source

## Completed Tasks
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T002`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T003`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P02-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P03-T001`

## Verification
- Command:
  - `Get-Content docs/architecture/runtime/modular-monolith-v2.md`
  - `Get-Content docs/architecture/runtime/modularity-audit-2026-03-19.md`
  - `rg -n "get_snapshot_engine\\(|src\\.(render|notify|telegram|services\\.attachments|entrypoints\\.http)" src`
- Result:
  - current code still matches the audit diagnosis that ownership facades exist but several technical clusters still compete as implementation centers

## Notes
- This campaign opens the architecture-recovery canon only.
- Later phases must remove or hard-deprecate at least one old path per wave.
- 2026-03-20: active top path no longer routes through `IndexDispatcher`; the dispatcher stays only as transitional compatibility code.
- 2026-03-20: `platform.runtime.queue_bootstrap` no longer wires domain jobs through direct `src.jobs/*` imports; job assembly now enters through owning context facades.

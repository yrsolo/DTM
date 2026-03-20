# Campaign Status Registry

Single source of truth for campaign lifecycle state.

## In Progress
- none

## Blocked
- CAM-2026-03-21-BOOTSTRAP-READABILITY-V1
- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## Done
- CAM-2026-03-21-DOCS-VOICE-UNIFICATION-V1 completed after removing the most visible future-facing and transitional wording from active docs so they read like current-system documentation.
- CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1 completed after rewriting active module docstrings in present-tense ownership language and renaming access-api query aliases away from broad snapshot-engine wording.
- CAM-2026-03-21-TOP-PATH-ELEGANCE-V1 completed after removing eager app-context access from `index.py`, keeping `src/entrypoint/handler.py` as the single top router, and aligning the closest top-path docs and tests.
- CAM-2026-03-21-REPO-BEAUTY-AUDIT-V1 completed after publishing the beauty assessment, the sequential backlog, and the smell-driven beauty-wave method used to execute the next curation steps.
- Pre-audit idealization wave completed as a safe polish pass over the active contour: docs, capability naming, and readability guardrails were aligned before external review.
- `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1` completed after replacing the active canon with module-first recovery, finishing the delta-audit-driven cleanup, moving snapshot internals under the snapshot context, removing `src/jobs/*`, and aligning active tests with module ownership under `tests/contexts/*`.
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1` completed after replacing the old architecture canon, removing the competing technical roots, and leaving `entrypoint -> platform/runtime -> owning context` as the active code map.
- `CAM-2026-03-19-MODULARITY-AUDIT-V1` completed after recording a code-verified module autonomy audit and decoupling plan.
- `CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1` completed after aligning the deploy guard with the active entrypoint contour and successfully rolling `dev` into `test`.
- `CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1` completed as the previous architecture wave and now serves as historical precedent rather than the current canon.
- `CAM-2026-03-16-DOCS-IA-REFRESH-V1` completed and archived after the docs information architecture refresh and link normalization wave.
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1` completed and archived after the legacy `.doc` preview split-flow and converter integration.
- Recent completed campaigns were archived under `work/archive/campaigns/`.
- Latest archived closeouts include the 2026-03-12 execution wave, 2026-03-14 attachment/people/audit waves, and the completed attachment cleanup wave.

## Planned
- none

## Parked
- CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1 (obsolete / already substantially delivered)

## Archived
- Completed campaigns were moved to `work/archive/campaigns/`.
- `agent/intructions/DTM-test/**` is treated as owner-provided reference input only.

## Rule
- Update this file first when campaign state changes.
- Keep `work/roadmap/backlog.md` aligned with the same state buckets.

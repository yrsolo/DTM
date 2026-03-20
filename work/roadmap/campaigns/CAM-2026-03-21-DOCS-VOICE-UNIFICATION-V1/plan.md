# CAM-2026-03-21-DOCS-VOICE-UNIFICATION-V1 Plan

Smell:
- several active docs still speak with recovery-era phrases such as `future refactor campaigns` or `Transitional extraction notes`

Target ideal:
- active docs describe the current system calmly and canonically, without sounding like an ongoing rescue

Kill criteria:
- active docs no longer use `Transitional extraction notes` in the active contour
- top-level active doc entrypoints no longer frame the canon as material only for future refactor campaigns
- touched docs read as current-system documentation rather than migration commentary

Scope boundary:
- selected active docs under `docs/README.md`, `docs/architecture/*`, and `docs/modules/*`
- no archive docs
- no campaign history rewrites outside link hygiene

Non-goals:
- no code changes
- no canon redesign
- no archive cleanup beyond active wording touchpoints

## Tasks

### P01 - Verify the active docs tone smell
- `CAM-2026-03-21-DOCS-VOICE-UNIFICATION-V1-P01-T001` verify the wording smell in the active docs contour against the beauty audit

### P02 - Remove recovery-era wording from active docs
- `CAM-2026-03-21-DOCS-VOICE-UNIFICATION-V1-P02-T001` replace active doc phrases that sound transitional or future-facing

### P03 - Verify and close
- `CAM-2026-03-21-DOCS-VOICE-UNIFICATION-V1-P03-T001` run grep-based verification and record a short verdict

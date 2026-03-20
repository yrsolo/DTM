# CAM-2026-03-21-ACTIVE-HISTORY-SEPARATION-V1 Plan

Smell:
- active runtime docs still surface archive/history material too early, which pulls the reader out of the active contour before it is necessary

Target ideal:
- active readers stay in the active runtime story by default and only drop into archive/history material intentionally

Kill criteria:
- active runtime docs no longer list historical predecessor files as part of the main deep-dive path
- archive/history notes stay present only as compact opt-in pointers
- touched active docs keep the current runtime story in the foreground

Scope boundary:
- active runtime docs only
- no archive rewrites
- no canon changes

Non-goals:
- no deletion of historical docs
- no changes to preserved precedent files

## Tasks

### P01 - Verify active/history smell
- `CAM-2026-03-21-ACTIVE-HISTORY-SEPARATION-V1-P01-T001` verify where archive/history is still too visible from active runtime docs

### P02 - Reduce archive visibility in active runtime docs
- `CAM-2026-03-21-ACTIVE-HISTORY-SEPARATION-V1-P02-T001` simplify archive/history pointers so they stay available but no longer compete with the active reading path

### P03 - Verify and close
- `CAM-2026-03-21-ACTIVE-HISTORY-SEPARATION-V1-P03-T001` run grep-based verification and record a short verdict

# CAM-HTTP-FALLBACK-REMOVAL-V1

## Goal
Remove HTTP fallback branches to legacy payload building. API v2 must be snapshot-only at runtime.

## Scope
- Remove prep-missing fallback to legacy in HTTP handlers.
- Return deterministic not-ready/unavailable response quickly.

## Phases and Tasks
### P01 - Remove fallback
- P01-T001: Remove legacy fallback branches in frontend v2 HTTP path.
- P01-T002: Standardize error payload (`frontend_source_unavailable` / `prep_not_ready`).

### P02 - Smoke and performance
- P02-T001: Validate cold path without prep snapshot.
- P02-T002: Verify response remains quick and deterministic.

### P03 - Evidence
- P03-T001: Record before/after handler behavior in campaign evidence.

## DoD
- HTTP runtime path does not call legacy payload builder.
- Missing snapshot does not trigger legacy rebuild in request path.

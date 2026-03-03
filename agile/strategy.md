# Agile Strategy

## Objective
Deliver DTM to stable production operation with clear, maintainable process artifacts.

## Current Focus (Stage 24 Proposal)
1. Promote Stage 23 cloud evidence into production-ready canary rehearsal package.
2. Close remaining marker gap (`meta.readmodelSource`) in v2 payload for clearer YDB contour observability.
3. Automate render/notify freshness evidence extraction from cloud logs.
4. Treat delivery as three equal product blocks:
   - Frontend API
   - Sheet Render
   - Notifications
   Each block must have explicit contract, smoke checks, and rollout knobs.

## Delivery Rules
- WIP=1 for execution tasks.
- Jira is optional; local control plane is `agile/sprint_current.md` + `agile/tasks/**`.
- Every stage ends with clear closeout and next-stage go/no-go.

## Constraints
- Preserve current business behavior in production contour.
- No secrets in git or console output.
- Small, reversible changes with smoke evidence.

## Metrics
- Deployment smoke pass rate.
- Reminder delivery SLI stability.
- Lead time from task start to done.
- Per-block readiness:
  - Frontend API: contract stability + endpoint smoke.
  - Sheet Render: fresh table timestamp + render smoke.
  - Notifications: delivery success/retry/error counters.

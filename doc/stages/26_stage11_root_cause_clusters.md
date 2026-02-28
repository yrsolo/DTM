# Stage 11 Root-Cause Clusters (Stages 0-10)

## Method
- Input: timeline (`doc/stages/25_stage11_timeline_reconstruction.md`), sprint/backlog history, incident artifacts.
- Grouping principle: recurrent mechanism, not isolated symptom.

## Cluster A: Configuration/Runtime Drift
- Signals:
  - missing runtime env/secret wiring in function versions,
  - local success but cloud failure due absent variables.
- Typical impact:
  - late failures in production path,
  - repeated hotfix deploy loops.
- Corrective direction:
  - mandatory preflight validation with explicit required keys,
  - single source for runtime contour + evidence snapshot per deploy.

## Cluster B: Late Failure Detection
- Signals:
  - key regressions visible only after deploy/runtime execution.
- Typical impact:
  - slow mean-time-to-diagnosis,
  - operator confusion due insufficiently normalized evidence.
- Corrective direction:
  - keep pre-deploy contract smoke gates,
  - keep normalized deploy run evidence report on every release.

## Cluster C: Process/Lifecycle Friction
- Signals:
  - execution pace interrupted by manual lifecycle drift (task state vs actual status),
  - blocked states discovered post-factum.
- Typical impact:
  - context lag and extra coordination overhead.
- Corrective direction:
  - strict WIP=1 and immediate blocked escalation,
  - mandatory completion note + counters update per task.

## Cluster D: Ownership And Operational Onboarding Gap
- Signals:
  - key runbook steps were chat-bound instead of doc-bound.
- Typical impact:
  - bus-factor risk and repeated clarification loops.
- Corrective direction:
  - owner quickstart checklist + rollback drill kept current as first-class artifacts.

## Next Slice Input
- Quantify recurrence and cost for each cluster.
- Convert to corrective backlog with owner/date/verification signal.

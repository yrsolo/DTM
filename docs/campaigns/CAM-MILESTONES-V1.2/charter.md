# CAM-MILESTONES-V1.2 Charter

## Problem
- R1: Full sync still writes legacy `dtm_task_milestones` in hot path, wasting YDB quota.
- R2: If `dtm_task_milestones_v` is missing for a task version, builder can return empty `tasks[].milestones`.
- R3: Version bump operations need safer ordering to reduce inconsistency risk without cross-table transactions.

## Goal
- Disable legacy milestones write by default (`compat only`).
- Guarantee non-empty milestones in readmodel (synthetic `start` fallback).
- Harden version bump path: no successful bump without written versioned milestones and consistent current version pointer.

## Non-goals
- No API v2 contract break.
- No global schema redesign.
- No cross-table transactional engine changes.

## Exit Criteria
- Sync skips legacy milestones write by default and logs skip reason.
- Builder guarantees at least one milestone (`start`) for every task.
- Version bump path fails fast on empty milestone writes and verifies `(task_id, current_version)` has rows.
- Forced refresh still does not mutate versions.
- Tests and evidence are published.

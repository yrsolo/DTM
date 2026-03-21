# CAM-MILESTONES-V1.1 Charter

## Problem
- Milestones are duplicated in two places:
  - `dtm_task_milestones`,
  - `dtm_tasks.raw_payload["milestones"]`.
- This allows source-of-truth drift and version mixing risk.
- Bulk milestone replace path previously used full-table delete, which is unsafe under partial failures.

## Goal
- Enforce versioned milestones as canonical source (`dtm_task_milestones_v`).
- Build readmodel milestones strictly by `(task_id, current_version)`.
- Keep sync path safe (no global delete on milestones table).
- Ship migration + verification evidence for existing data.

## Non-goals
- No Google Sheets format redesign.
- No breaking changes for API v2 response structure.
- No event-sourcing redesign.

## Exit Criteria
- Readmodel does not use `raw_payload["milestones"]` as source of truth.
- `dtm_task_milestones_v` is populated and used in runtime path.
- Sync path has no global wipe delete for milestones.
- Migration script exists and supports legacy->versioned transfer with raw fallback.
- Evidence and tests confirm version-consistent milestone behavior.

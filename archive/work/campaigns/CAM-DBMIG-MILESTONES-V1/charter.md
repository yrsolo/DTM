# CAM-DBMIG-MILESTONES-V1 Charter

## Problem
- Milestone timings can diverge from task content versions.
- Current and archived timing states risk being mixed when building readmodel payloads.

## Goal
- Make readmodel milestone source deterministic by `(task_id, current_version)`.
- Ensure runtime cannot read task content from one version and milestones from another.
- Keep forced refresh behavior version-safe (no version bump for existing tasks).

## Non-goals
- No external API contract break for v1/v2 routes.
- No Google Sheets structure redesign.

## Exit Criteria
- Versioned milestones table is in active schema and write/read paths use it.
- Readmodel builder reads milestones strictly by `current_version`.
- Forced refresh rebuilds snapshots without version increments.
- Tests and evidence confirm no cross-version timing mix.


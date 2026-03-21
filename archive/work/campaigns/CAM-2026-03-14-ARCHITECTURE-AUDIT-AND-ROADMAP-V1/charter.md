# CAM-2026-03-14-ARCHITECTURE-AUDIT-AND-ROADMAP-V1 Charter

## Problem
- the active runtime is directionally cleaner than the planner-era system, but it is not obvious how close it is to the intended clean, snapshot-first, queue-backed architecture
- `index.py` feels suspicious, but current evidence suggests the real architectural debt may sit elsewhere
- the team needs a code-backed answer, not intuition, about what is already good, what is transitional, and what should be refactored first

## Goal
- produce a current-truth architecture audit of the active runtime
- score the main runtime subsystems against the target architectural values
- identify prioritized architectural debt with practical impact
- deliver a decision-complete 3-5 wave refactor roadmap

## Non-goals
- this campaign does not refactor runtime code
- this campaign does not change behavior, interfaces, or deployment
- this campaign does not reopen legacy/YDB architecture as a candidate target model

## Exit Criteria
- one top-level architecture verdict exists
- one subsystem scorecard exists
- one prioritized findings list exists
- a multi-wave refactor roadmap exists with explicit first and second waves
- the audit explicitly answers:
  - whether `index.py` is actually dirty
  - where the main architectural dirt really sits
  - what should be touched first

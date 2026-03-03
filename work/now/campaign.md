# CAM-PIPELINE-CLEAN-SKELETON-V1

## Status
Activated from priority queue after CAM-CONFIG-REFORM-V0 core milestones.

## Goal
Make runtime pipeline skeleton linear and predictable: context + use-case contracts + thin orchestration.

## Current Phase
P04: closeout + handoff preparation.

## Important Rule
- Keep business behavior unchanged while introducing contracts/scaffold.

## Exit Criteria
- `AppContext` contract and use-case contracts exist and are wired in bootstrap.
- `TimerJob` shell is integrated into runtime path without behavior regressions.
- Typed error taxonomy exists and is mapped at entrypoint boundary.
- System docs reflect the transition state and next campaign handoff.

## Archive
- closeouts stored in `work/archive/campaigns/*/closeout.md`.

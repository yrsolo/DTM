# Designers Task Manager (DTM)

DTM is an automation service for design-team planning around Google Sheets.
It is moving toward a snapshot-first, queue-backed, browser-safe runtime that serves prepared read paths and async command execution from one data contour.

## Core capabilities
- Ingest and normalize tasks/milestones from Google Sheets.
- Build and publish prepared frontend-ready snapshots.
- Serve HTTP API for web clients and operational views.
- Render planning views and run reminder flows for Telegram.
- Apply optional LLM-based message styling (`openai`, `google`, `yandex`).

## Architecture (high level)
Flow: `Sheets -> Raw Snapshot -> Prep Snapshot -> Read/API/Render/Notify + Queue-backed mutations`.
The project is actively removing planner-centric runtime assumptions and import-time bootstrap side effects.
Deploy target is Yandex Cloud Function with test/prod contours.

Current architecture policy and wave guidance:
- [docs/system/architecture_values.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/architecture_values.md)
- [docs/system/architecture.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/architecture.md)
- [work/roadmap/MASTER_EXECUTION_BRIEF_2026-03-12.md](/n:/PROJECTS/python/SCRIPT/DTM/work/roadmap/MASTER_EXECUTION_BRIEF_2026-03-12.md)

## Context
Data volume is moderate (historical around 1000 tasks, active subset smaller).
Hourly-level synchronization is sufficient for current business cadence.

## Entry points
- Documentation map: `docs/README.md`
- Process/campaign map: `work/README.md`
- Current campaign status: `work/now/README.md`

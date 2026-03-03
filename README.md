# Designers Task Manager (DTM)

DTM is an automation service for design-team planning around Google Sheets.
It keeps operational task data in YDB, publishes readmodels, and serves multiple consumers from one data contour.

## Core capabilities
- Ingest and normalize tasks/milestones from Google Sheets.
- Build and publish frontend-ready readmodel snapshots.
- Serve HTTP API (`/api/v1`, `/api/v2`) for web clients.
- Render planning views and run reminder flows for Telegram.
- Apply optional LLM-based message styling (`openai`, `google`, `yandex`).

## Architecture (high level)
Flow: `Ingest -> Normalize -> YDB operational store -> Readmodel -> API/Render/Notify`.
The project is migrating from legacy contours to a unified readmodel-first runtime.
Deploy target is Yandex Cloud Function with test/prod contours.

## Context
Data volume is moderate (historical around 1000 tasks, active subset smaller).
Hourly-level synchronization is sufficient for current business cadence.

## Entry points
- Documentation map: `docs/README.md`
- Process/campaign map: `work/README.md`
- Current campaign status: `work/now/README.md`

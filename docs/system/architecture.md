# Architecture (Current)

## Purpose
DTM (Designers Task Manager) synchronizes a Google Sheets task table into YDB, builds a **frontend readmodel snapshot**, and uses it to serve/produce:
- API responses (frontend v2 payload)
- Sheets rendering (views/diagrams)
- Telegram reminders (optionally LLM-styled)

## Canonical pipeline
**Sheets snapshot (values + colors) → Normalize → Hash/Version → YDB operational tables → Build readmodel snapshot → Consumers**

Key property: consumers SHOULD NOT depend on Sheets directly; they use a DB snapshot (readmodel) or operational bulk reads.

## Entrypoints
- `index.py` — HTTP entrypoint (serverless handler). Routes API and other HTTP calls.
- `main.py` — job runner (timer sync/build, render, notify, migrate).
- `local_run.py` — local wrapper for running modes.

## Main subsystems

### Source ingestion (Sheets)
- Reads:
  - raw values (cells)
  - colors/status markers (used as status/phase signal)

### Normalization (domain)
Transforms sheet rows into canonical normalized tasks:
- stable fields (title/brand/format/customer/owner/group/raw_timing/etc.)
- milestones list (planned/actual/status/raw_text/confidence)
- status derived from colors mapping

### Operational storage (YDB)
YDB stores:
- Head state for tasks (`dtm_tasks`)
- Version history (`dtm_task_versions`)
- Versioned milestones per task revision (`dtm_task_milestones_v`)
- Sync cursor/metadata (`dtm_sync_state`)
- Readmodel snapshot row (`dtm_readmodel_frontend_v2`)

### Readmodel snapshot
Readmodel builder loads operational data in bulk and writes a single JSON payload row:
- API v2 reads this snapshot (1 query) instead of rebuilding on the fly.

## Design constraints
- Sheets file modified time is unreliable (renderer updates same file). Hash gate must be on **source-range values/colors**.
- YDB serverless quota: avoid N+1 queries; prefer bulk reads/writes.
- Timing changes are significant: milestones changes must trigger version bump.

## Target (future) style for entrypoints
`index.py`/`main.py` should be thin: parse mode/request, call one handler/use-case, return output.
All flags/if-ladders should be buried into config/strategies/services.

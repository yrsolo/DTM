# Architecture (Current)

DTM runtime pipeline:
1. Read source data from Google Sheets.
2. Normalize tasks and milestones.
3. Store operational state in YDB.
4. Build frontend readmodel snapshot.
5. Serve API/render/notify consumers.

Main runtime entrypoints:
- `index.py` for HTTP/API-gateway requests.
- `main.py` and `local_run.py` for timer/sync/reminder jobs.

Historical architecture iterations are in `docs/archive/doc_legacy/stages/`.

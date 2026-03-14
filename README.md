# Designers Task Manager (DTM)

DTM is a snapshot-first, queue-backed automation service for design-team planning around Google Sheets.

Current runtime shape:
- reads tasks and people data from Google Sheets,
- builds Raw/Prep snapshots in Object Storage,
- serves browser/API reads from prepared snapshots,
- runs heavy mutations asynchronously through queue-backed jobs,
- renders Sheets views and sends Telegram reminders from the same snapshot contour.

Current runtime defaults:
- `index.py` is a thin shell,
- read paths are browser-safe and side-effect free,
- `/info` is summary-first by default,
- browser auth and masking stay at the HTTP boundary,
- render/refresh/reminder work happens through async commands or explicit runtime modes.

Start here:
- [docs/system/architecture.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/architecture.md)
- [docs/system/module_map.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/module_map.md)
- [docs/system/config.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/config.md)
- [docs/system/runbook.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/runbook.md)
- [docs/system/browser_auth_runbook.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/browser_auth_runbook.md)

Documentation/process maps:
- [docs/README.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/README.md)
- [work/README.md](/n:/PROJECTS/python/SCRIPT/DTM/work/README.md)
- [work/now/README.md](/n:/PROJECTS/python/SCRIPT/DTM/work/now/README.md)

Legacy and migration-era material is intentionally kept out of the current narrative.
If historical detail is needed, use `docs/archive/*` and `work/archive/*`.

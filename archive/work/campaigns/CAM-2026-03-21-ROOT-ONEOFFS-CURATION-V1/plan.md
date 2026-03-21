# CAM-2026-03-21-ROOT-ONEOFFS-CURATION-V1

## Goal
- Remove root-level one-off files that no longer belong to the active repo surface.

## Scope
- Archive `run_alert_eval_ci.cmd` if it is disconnected from live runtime/CI/operator scenarios.
- Remove duplicate root `profile_runtime_path.py` because the only surviving value is historical and already belongs in archive notebooks.
- Remove root `__pycache__/`.
- Refresh local tracking after the cut.

## Out of Scope
- Reworking the still-live `run_timer.cmd` wrapper used by deploy workflows.
- Any change to `agile/README.md`.
- Any edits under `agent/intructions/`.

## Acceptance
- Active root no longer contains disconnected one-off files.
- Historical one-off command remains available under `archive/work/`.
- Tracking records the cut and the verification source.

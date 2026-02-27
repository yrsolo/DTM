# Baseline Validation And Artifacts (Stage 0.4)

## Purpose
Define a repeatable baseline validation flow so behavior regressions are detected before merge.

## Capture Command
Run from repository root:

```powershell
.venv\Scripts\python.exe agent\capture_baseline.py --label pre_change
```

Default command executed by helper:

```powershell
.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run
```

## Artifact Structure
Helper stores output in:

`artifacts/baseline/<UTC_TIMESTAMP>_<label>/`

Files:
- `sync_dry_run.log` - stdout/stderr from dry-run execution.
- `meta.json` - command, git sha, timestamp, exit code.
- `CHECKLIST.md` - validation checklist to compare with previous baseline.

## Mandatory Comparison Points
- Row/column counts in target sheets.
- Values of key milestone cells.
- Presence of notes and colors in sampled cells.
- Runtime stability (exit code and error-free log tail).

## TeamLead Process
1. Capture baseline before change set.
2. Capture baseline after change set.
3. Compare artifact bundles and mark checklist items.
4. Post short evidence summary in Jira and task work log.

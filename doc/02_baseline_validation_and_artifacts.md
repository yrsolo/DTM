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
.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run --evaluate-alerts --alert-fail-profile local --alert-evaluation-file artifacts\baseline\<...>\alert_evaluation.json --quality-report-file artifacts\baseline\<...>\quality_report.json
```

By default helper uses local-safe alert gate profile (`--alert-fail-profile local`, effective fail gate `none`).

Optional controlled notify trigger (explicit opt-in only):

```powershell
.venv\Scripts\python.exe agent\capture_baseline.py --label pre_change --notify-owner-on critical
```

## Artifact Structure
Helper stores output in:

`artifacts/baseline/<UTC_TIMESTAMP>_<label>/`

Files:
- `sync_dry_run.log` - stdout/stderr from dry-run execution.
- `quality_report.json` - structured quality diagnostics snapshot from runtime.
- `alert_evaluation.json` - evaluator result (`level`, `reason`, summary metrics, thresholds).
- `meta.json` - command, git sha, timestamp, exit code.
- `CHECKLIST.md` - validation checklist to compare with previous baseline.

## Mandatory Comparison Points
- Row/column counts in target sheets.
- Values of key milestone cells.
- Presence of notes and colors in sampled cells.
- Runtime stability (exit code and error-free log tail).
- Alert level classification and reason (`INFO_ONLY/WARN/CRITICAL/OK`) versus expected sample size.

## TeamLead Process
1. Capture baseline before change set.
2. Capture baseline after change set.
3. Compare artifact bundles (`quality_report.json` + `alert_evaluation.json`) and mark checklist items.
4. If alert level changed unexpectedly, create/update risk follow-up item in sprint notes before merge.
5. Post short evidence summary in Jira and task work log.

## Routine Ops Cadence Checklist (Stage 5)
Use this cadence to keep threshold tuning reproducible and avoid ad-hoc policy drift.

### Per run
- Execute baseline helper and confirm `quality_report.json` + `alert_evaluation.json` exist.
- Record evaluated level (`INFO_ONLY/WARN/CRITICAL/OK`) and core metrics in Jira evidence comment.
- If level is `WARN` or `CRITICAL`, apply escalation policy from `doc/05_risk_register.md`.

### Weekly
- Review the latest 3+ baseline bundles and check for repeated false-positive/false-negative patterns.
- Verify evaluator gate profile usage is consistent:
  - CI checks use `--fail-profile ci`.
  - local review stays non-blocking with `--alert-fail-profile local` unless explicitly overridden.
- Update `agile/sprint_current.md` notes with summary decision (`no tuning` or `tuning proposed`).

### Monthly
- Run a threshold drift review with trend snapshots and baseline artifacts.
- If tuning is needed, create a dedicated Jira task (separate from notifier-behavior changes).
- Document rationale and before/after examples in task file + Jira before applying any threshold update.

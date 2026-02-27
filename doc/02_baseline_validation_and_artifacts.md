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
.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run --evaluate-alerts --alert-fail-profile local --alert-evaluation-file artifacts\baseline\<...>\alert_evaluation.json --quality-report-file artifacts\baseline\<...>\quality_report.json --read-model-file artifacts\baseline\<...>\read_model.json --read-model-build-id baseline-<label>
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
- `read_model.json` - canonical Stage 6 read-model artifact for UI/API planning flow.
- `meta.json` - command, git sha, timestamp, exit code.
- `CHECKLIST.md` - validation checklist to compare with previous baseline.

Cloud note:
- For serverless runtime (Yandex Cloud function), baseline artifact files in local filesystem are dev-only.
- Cloud-profile artifacts should be uploaded to Yandex Object Storage (S3-compatible) as primary storage.
- Policy reference: `doc/15_stage7_read_model_consumer_policy.md`.

## Mandatory Comparison Points
- Row/column counts in target sheets.
- Values of key milestone cells.
- Presence of notes and colors in sampled cells.
- Runtime stability (exit code and error-free log tail).
- Alert level classification and reason (`INFO_ONLY/WARN/CRITICAL/OK`) versus expected sample size.

## TeamLead Process
1. Capture baseline before change set.
2. Capture baseline after change set.
3. Compare artifact bundles (`quality_report.json`, `alert_evaluation.json`, `read_model.json`) and mark checklist items.
4. If alert level changed unexpectedly, create/update risk follow-up item in sprint notes before merge.
5. Post short evidence summary in Jira and task work log.

## Routine Ops Cadence Checklist (Stage 5)
Use this cadence to keep threshold tuning reproducible and avoid ad-hoc policy drift.

### Per run
- Execute baseline helper and confirm `quality_report.json`, `alert_evaluation.json`, and `read_model.json` exist.
- Record evaluated level (`INFO_ONLY/WARN/CRITICAL/OK`) and core metrics in Jira evidence comment.
- If level is `WARN` or `CRITICAL`, apply escalation policy from `doc/05_risk_register.md`.
- Verify retry taxonomy metrics in `quality_report.summary`:
  - `reminder_send_retry_attempt_count`
  - `reminder_send_retry_exhausted_count`
  - `reminder_send_error_transient_count`
  - `reminder_send_error_permanent_count`
  - `reminder_send_error_unknown_count`

### Weekly
- Review the latest 3+ baseline bundles and check for repeated false-positive/false-negative patterns.
- Verify evaluator gate profile usage is consistent:
  - CI checks use `run_alert_eval_ci.cmd`.
  - local review stays non-blocking with `--alert-fail-profile local` unless explicitly overridden.
- Review retry taxonomy mix:
  - `transient` dominates only during temporary incidents,
  - `permanent` spikes indicate data/chat-id issues,
  - `unknown` > 0 requires classifier follow-up task.
- Apply weekly trend thresholds for retry taxonomy:
  - `reminder_send_retry_exhausted_count >= 3` for the week -> create mitigation task.
  - `reminder_send_error_unknown_count >= 1` in two consecutive weekly reviews -> create classifier tuning task.
  - `reminder_send_error_permanent_count >= 3` and `permanent >= transient` -> create data quality follow-up task.
- Update `agile/sprint_current.md` notes with summary decision (`no tuning` or `tuning proposed`).

### Monthly
- Run a threshold drift review with trend snapshots and baseline artifacts.
- If tuning is needed, create a dedicated Jira task (separate from notifier-behavior changes).
- Document rationale and before/after examples in task file + Jira before applying any threshold update.

# Risk Register

## Format
- `id`
- `risk`
- `probability` (`low|medium|high`)
- `impact` (`low|medium|high|critical`)
- `mitigation`
- `owner`
- `status` (`open|mitigated|watch`)
- `notes`

## Active Risks
1. `R-001`
- risk: write into production target sheet from local/dev run.
- probability: medium
- impact: critical
- mitigation: separated `SOURCE_SHEET_NAME` / `TARGET_SHEET_NAME`, `ENV` guard, `--dry-run` verification flow.
- owner: tech lead
- status: open
- notes: residual operational risk remains if env contour is configured incorrectly.

2. `R-002`
- risk: secret leak (tokens/keys/proxy creds) in git history.
- probability: medium
- impact: critical
- mitigation: detect-secrets pre-commit gate, `.env` handling rules, security checklist.
- owner: tech lead
- status: open
- notes: continuous hygiene risk, requires permanent enforcement.

3. `R-003`
- risk: duplicate Telegram reminder sends on repeated trigger in same run.
- probability: low
- impact: high
- mitigation: in-run idempotency delivery key (`date+designer+chat+message_hash`) in reminder pipeline.
- owner: backend
- status: mitigated
- notes: implemented in Stage 4 (`DTM-33`), monitor via `skipped_duplicate` counter.

4. `R-004`
- risk: timezone/date boundary errors (wrong day/deadline).
- probability: medium
- impact: high
- mitigation: normalized date logic in reminder flow, deterministic smoke checks for active modes.
- owner: backend
- status: watch
- notes: keep boundary tests in smoke regression set.

5. `R-005`
- risk: Google API quota/rate degradation affects sync pipeline.
- probability: medium
- impact: high
- mitigation: dry-run safe verification, operational fallback to rerun; explicit retry/backoff policy still pending.
- owner: backend
- status: open
- notes: retry/backoff policy is backlog item, not fully implemented yet.

6. `R-006`
- risk: OpenAI enhancer unavailable or slow, reminder quality degrades or flow stalls.
- probability: medium
- impact: medium
- mitigation: fallback to deterministic draft, bounded parallel enhancer concurrency, mock-external test mode.
- owner: backend
- status: mitigated
- notes: delivery continuity preserved even when enhancer fails (`DTM-32`, `DTM-35`).

7. `R-007`
- risk: Telegram transient delivery failures without explicit retry policy.
- probability: medium
- impact: high
- mitigation: bounded retry/backoff policy for transient send failures with retry/exhausted counters in quality report.
- owner: backend
- status: watch
- notes: implemented in Stage 5 (`DTM-41`) and transient/permanent/unknown send-error taxonomy tuned in `DTM-45`; monitor retry exhaustion rate and taxonomy drift.

8. `R-008`
- risk: insufficient operational visibility for reminder incidents.
- probability: medium
- impact: medium
- mitigation: structured delivery counters + derived SLI fields in quality report summary.
- owner: tech lead
- status: watch
- notes: alert thresholds and escalation policy formalized in Stage 5 (`DTM-39`).

## Reminder Alerting Thresholds And Escalation Policy

### Metrics source
- `quality_report.summary.reminder_delivery_rate`
- `quality_report.summary.reminder_failure_rate`
- `quality_report.summary.reminder_delivery_attemptable_count`
- `quality_report.summary.reminder_send_error_count`

### Thresholds
- `WARN`: `reminder_delivery_attemptable_count >= 5` and `reminder_delivery_rate < 0.98`.
- `CRITICAL`: `reminder_delivery_attemptable_count >= 5` and (`reminder_delivery_rate < 0.95` or `reminder_send_error_count >= 3`).
- `INFO_ONLY`: `reminder_delivery_attemptable_count < 5` (insufficient sample size for hard alerting).

### Escalation sequence
1. Generate quality report after each run and evaluate thresholds.
   - baseline automation helper: `python agent/reminder_alert_evaluator.py --fail-profile ci` (latest artifact auto-discovery, CI gate).
   - local review default should stay non-blocking via `local_run.py --alert-fail-profile local` unless explicit override is needed.
2. On `WARN`: create/update Jira incident follow-up task and post evidence comment with metrics snapshot.
3. On `CRITICAL`: immediately notify owner via `python agent/notify_owner.py` with Russian text and explicit next action options.
   - controlled runtime trigger: use evaluator/local-run flag `--notify-owner-on critical` (default remains `none`).
   - RU-only payload validation is enforced by `agent/notify_owner.py` for title/details/options/context.
4. Keep affected sprint item in `agile/sprint_current.md` under `Blocked` until owner decision is received.

### Owner next action template (for notify message)
- `1) create a new chat for incident mitigation task`
- `2) reply to TeamLead to continue current chat with selected option`

### Threshold tuning loop (Stage 5 ops)
1. Collect at least 3 recent baseline bundles with both `quality_report.json` and `alert_evaluation.json`.
2. Track distribution of `reminder_delivery_attemptable_count`, `reminder_delivery_rate`, `reminder_send_error_count`, and evaluated `level`.
3. Propose threshold adjustment only when false-positive or false-negative pattern is observed in at least 2 consecutive runs.
4. For each proposed tuning change:
   - document rationale and before/after examples in task file and Jira comment,
   - update this policy section and `agile/sprint_current.md` notes,
   - run evaluator smoke and one real dry-run sanity command.
5. Do not change thresholds and notifier behavior in the same iteration; split policy tuning and runtime behavior changes into separate tasks.

### Routine cadence enforcement
- `Per run`: execute baseline/evaluator flow, log evaluated level and metrics in Jira evidence.
- `Weekly`: review latest 3+ bundles and decide `no tuning` vs `tuning proposed`; apply retry taxonomy trend thresholds:
  - `reminder_send_retry_exhausted_count >= 3` -> mitigation follow-up task.
  - `reminder_send_error_unknown_count >= 1` in two consecutive weekly reviews -> classifier tuning task.
  - `reminder_send_error_permanent_count >= 3` with `permanent >= transient` -> data quality follow-up task.
- `Monthly`: run threshold drift review and create dedicated Jira task for any threshold update.
- Operational checklist source of truth: `doc/ops/baseline_validation_and_artifacts.md` (Routine Ops Cadence Checklist).

### Retry taxonomy metrics checklist
- Metrics to review from `quality_report.summary`:
  - `reminder_send_retry_attempt_count`
  - `reminder_send_retry_exhausted_count`
  - `reminder_send_error_transient_count`
  - `reminder_send_error_permanent_count`
  - `reminder_send_error_unknown_count`
- Interpretation rules:
  - sustained growth of `retry_exhausted` means transient incident is not recovering and requires mitigation task,
  - high `permanent` share points to data/contact quality issues (chat_id/access),
  - any non-zero `unknown` requires taxonomy follow-up and classifier review task.
- Weekly threshold note:
  - use explicit weekly trigger values from `Routine cadence enforcement` before deciding `tuning proposed`.

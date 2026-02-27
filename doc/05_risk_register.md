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
- notes: implemented in Stage 5 (`DTM-41`); monitor retry exhaustion rate and tune limits.

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
2. On `WARN`: create/update Jira incident follow-up task and post evidence comment with metrics snapshot.
3. On `CRITICAL`: immediately notify owner via `python agent/notify_owner.py` with Russian text and explicit next action options.
4. Keep affected sprint item in `agile/sprint_current.md` under `Blocked` until owner decision is received.

### Owner next action template (for notify message)
- `1) create a new chat for incident mitigation task`
- `2) reply to TeamLead to continue current chat with selected option`

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
- mitigation: current handling logs errors and counts `send_errors`; explicit retry/backoff policy is pending.
- owner: backend
- status: open
- notes: next step is controlled retry strategy with bounded attempts and jitter.

8. `R-008`
- risk: insufficient operational visibility for reminder incidents.
- probability: medium
- impact: medium
- mitigation: structured delivery counters + derived SLI fields in quality report summary.
- owner: tech lead
- status: watch
- notes: alert thresholds/escalation policy still pending Stage 5 follow-up.

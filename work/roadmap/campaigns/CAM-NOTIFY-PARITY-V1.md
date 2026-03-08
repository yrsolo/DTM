# CAM-NOTIFY-PARITY-V1

## Goal
Restore legacy reminder business behavior in the new `src/notify/*` contour on top of Snapshot Engine, without returning to legacy planner runtime.

## Scope
- Snapshot-based people routing for notify (name -> chat_id/vacation/position).
- Reminder selection parity: milestones on today and next workday.
- Draft message parity + LLM enhancement with fallback to draft.
- Telegram delivery parity: vacation/chat checks, retries/backoff, error classification, dedup.
- Structured runtime result for `reminder_v2`, `reminders-only`, `morning`, `test`.

## Non-goals
- No API v2 payload contract changes.
- No reintroduction of legacy `core.reminder` into runtime path.
- No tuning-only prompt improvements beyond parity core.

## Phases and Tasks
### P01 - Trust gate and parity freeze
- P01-T001: Verify current runtime behavior against code and freeze legacy parity baseline.

### P02 - Snapshot people contour
- P02-T001: Add people snapshot model/interfaces/S3 store wiring.
- P02-T002: Add people snapshot update path (sheet `Люди` -> snapshot object).
- P02-T003: Wire people snapshot access through bootstrap/snapshot engine.

### P03 - Selection parity
- P03-T001: Implement today + next workday milestone-based selection.
- P03-T002: Keep default active statuses (`work`, `pre_done`) and strict milestone intersection.

### P04 - Draft + LLM parity
- P04-T001: Implement legacy-like draft message sections and stage filtering.
- P04-T002: Implement async enhancement with counters and fallback-to-draft.

### P05 - Delivery parity
- P05-T001: Resolve targets from people snapshot with vacation/chat checks.
- P05-T002: Add retry/backoff/error classification and per-run dedup.
- P05-T003: Enforce test contour delivery to test chat only.

### P06 - Runtime integration
- P06-T001: Route `reminder_v2/reminders-only/morning/test` through new parity job.
- P06-T002: Return structured JSON counters in runtime response.

### P07 - Config
- P07-T001: Add typed notify parity settings in `config/runtime.yaml` + loader/schema.

### P08 - Tests and docs
- P08-T001: Add notify parity unit tests (selection/formatter/delivery/llm).
- P08-T002: Add people snapshot tests.
- P08-T003: Update runbook/dataflow and campaign evidence.

## DoD
- New notify path selects designers only by milestones on today/next workday.
- Routing is snapshot-people based with vacation/chat checks.
- LLM enhancement fallback is deterministic and counted.
- Delivery retries/backoff/classification/dedup parity is implemented.
- Runtime response includes real counters for reminder modes.
- Tests for parity logic are green.

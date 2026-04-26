# Evidence

## Trust Gate

- source: `src/platform/runtime/orchestration.py`, `src/contexts/reminders/internal/job_runner.py`, `src/entrypoints/runtime/planner_runtime_entry.py`, `config/llm.yaml`
- last_verified_at: 2026-04-26
- verified_by: Codex
- evidence: `morning` trigger enqueues `send_reminders`; queued and direct planner reminder paths pass `cfg.llm.models["openai_default"]` into the reminder enhancer today.
- trust_level: high
- notes: Active code paths were checked directly against runnable Python modules, not inferred from docs.

- source: OpenAI API models docs
- last_verified_at: 2026-04-26
- verified_by: Codex
- evidence: Official docs list GPT-5.5 with model ID `gpt-5.5`; OpenAI launch page also states API availability for `gpt-5.5`.
- trust_level: high
- notes: Used only to confirm the current API model ID before changing config.

## Verification

- 2026-04-26: `python -m pytest tests/contexts/reminders/test_reminder_model_selection.py tests/contexts/reminders/test_send_reminders_job.py tests/entrypoints/test_planner_runtime_entry.py tests/platform/test_orchestration.py -q` passed, 17 tests.
- 2026-04-26: `python -m pytest tests/config/test_runtime_loader.py tests/architecture/test_guardrails_v0.py -q` passed, 55 tests.
- 2026-04-26: Follow-up config load check printed `openai_default=gpt-4o` and `openai_by_mode={'morning': 'gpt-5.5'}`.

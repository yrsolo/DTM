# Stage 18 Enhancer Counters And Smoke

## New reminder enhancer counters
- `provider`
- `candidates_total`
- `attempted`
- `succeeded`
- `fallback_empty`
- `fallback_exception`
- `skipped_mock`

## Quality report integration
- Added to `summary`:
  - `reminder_enhancer_provider`
  - `reminder_enhancer_candidate_count`
  - `reminder_enhancer_attempt_count`
  - `reminder_enhancer_success_count`
  - `reminder_enhancer_fallback_empty_count`
  - `reminder_enhancer_fallback_exception_count`
  - `reminder_enhancer_skipped_mock_count`
- Added full payload section:
  - `reminder_enhancement_counters`

## Smoke evidence
- `.venv\Scripts\python.exe -m compileall config core agent main.py`
- `.venv\Scripts\python.exe -m agent.reminder_fallback_smoke`
- `.venv\Scripts\python.exe -m agent.reminder_enhancer_counters_smoke`
- `.venv\Scripts\python.exe -m agent.llm_provider_bootstrap_smoke`

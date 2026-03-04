# Reminder Transport Extraction Plan (Core Cleanup)

## Goal
Move external transport clients out of `core/reminder.py` while preserving reminder behavior and retries.

## Current mixed areas in `core/reminder.py`
- Domain/application logic:
  - reminder selection and grouping
  - message template assembly and fallback policy
  - delivery/enhancement counters
- Infra logic:
  - Telegram SDK client (`telegram.ext.Application`)
  - OpenAI SDK client (`openai.AsyncOpenAI`)
  - direct HTTP clients (`httpx`, `aiohttp`)

## Atomic extraction sequence
1. Extract pure helper functions from `core/reminder.py` into `core/reminder_policy.py`:
   - message normalization,
   - transient error classification,
   - lightweight formatting utilities.
2. Move transport adapters to `src/adapters/llm_*.py` and `src/adapters/telegram.py`:
   - `AsyncOpenAIChatAgent`,
   - `AsyncGoogleLLMChatAgent`,
   - `AsyncYandexLLMChatAgent`,
   - `TelegramNotifier`.
3. Keep `FallbackChatAdapter` and `Reminder` in core for now, but switch imports to adapter modules.
4. Leave compatibility re-exports in `core/reminder.py` for legacy imports.
5. After import switch stability, split `Reminder` orchestration into `src/services/notify/reminder_runtime.py`.

## Risk controls
- Do not change retry thresholds/backoff in the same step as code movement.
- Preserve exact counter keys in `get_delivery_counters` and `get_enhancement_counters`.
- Keep API signatures of exported classes during shim phase.

## Safety checks per step
- `python -m py_compile core/reminder.py src/adapters/llm_openai.py src/adapters/llm_google.py src/adapters/llm_yandex.py src/adapters/telegram.py`
- `python -m unittest tests.services.test_pipeline_runtime -v`
- if environment has optional deps installed: `python -m unittest tests.api.test_frontend_api_routing -v`

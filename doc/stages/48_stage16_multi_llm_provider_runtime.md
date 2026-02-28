# Stage 16 Multi-LLM Provider Runtime

## Scope delivered
- Added runtime provider switch:
  - `LLM_PROVIDER=openai|google|yandex`
- Added provider-specific adapter config:
  - OpenAI: `OPENAI_TOKEN`, `OPENAI_MODEL`
  - Google: `GOOGLE_LLM_API_KEY`, `GOOGLE_LLM_MODEL`
  - Yandex: `YANDEX_LLM_API_KEY`, `YANDEX_LLM_MODEL_URI`

## Implementation details
- `config/constants.py`
  - Added `ALLOWED_LLM_PROVIDERS` validation.
  - Added provider env variables and Yandex model URI fallback from `YC_FOLDER_ID`.
- `core/reminder.py`
  - Kept `AsyncOpenAIChatAgent` contract unchanged.
  - Added `AsyncGoogleLLMChatAgent` (Generative Language API).
  - Added `AsyncYandexLLMChatAgent` (Foundation Models API).
  - Added shared message normalization helper for adapter inputs.
- `core/bootstrap.py`
  - `_build_chat_adapter()` now routes adapter creation by `LLM_PROVIDER`.
  - `mock_external=True` behavior unchanged and still returns `MockOpenAIChatAgent`.

## Compatibility notes
- Existing OpenAI flow remains default (`LLM_PROVIDER` default is `openai`).
- Reminder orchestration contract (`ChatAdapter.chat(messages, model=None)`) remains unchanged.
- No cross-provider fallback chain added in this stage.

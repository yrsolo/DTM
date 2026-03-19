# Runtime Canon

## Top path

The top path must be readable in 1-2 screens:
- `index.py`
- `src/entrypoint/*`
- `src/platform/runtime/*`
- owning module facade

## Runtime responsibilities

Runtime owns:
- input classification
- explicit mode routing
- explicit command routing
- orchestration of triggers and invalidation jobs
- diagnostics and operator surfaces

Runtime does not own:
- business rules
- module-specific policy
- long-lived domain assembly logic

## Top-path quality bar

A reader should be able to identify:
- how the scenario enters the system
- which module owns it
- where the use case executes

If that still requires following multiple delegator chains through technical clusters, the top path is not yet healed.

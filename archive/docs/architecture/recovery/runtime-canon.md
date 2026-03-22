# Runtime Canon

## Top path

The top path must be readable in 1-2 screens:
- `index.py`
- `src/entrypoints/root/*`
- `src/platform/shell/*`
- owning module facade

For browser task-card reads, the canonical path is read-side delivery:
- mutation may start elsewhere, but card visibility is judged through `snapshot` projection and `access_api` cached delivery
- upload-only or finalize-only paths are not the canonical end of the browser scenario

## Runtime responsibilities

Runtime owns:
- input classification
- explicit mode routing
- explicit command routing
- orchestration of triggers and invalidation jobs
- diagnostics and operator surfaces
- orchestration that connects mutation completion to read-side freshness

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

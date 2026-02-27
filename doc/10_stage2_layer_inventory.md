# Stage 2 Layer Inventory (Current State)

## Purpose
Document the current module boundaries for Stage 2 decomposition and identify the first low-risk extraction slice.

## Layer Model
- `interfaces`: runtime entrypoints and invocation contract (`main.py`, `local_run.py`, `index.py`).
- `application`: orchestration use-cases coordinating repositories, services, reminders.
- `domain`: pure business rules/data structures without direct external API calls.
- `infrastructure`: adapters for Google Sheets, Telegram, OpenAI, cloud runtime, and external transport.

## Current Module-to-Layer Inventory

### interfaces
- `main.py`
  - Resolves mode/event and executes sync/reminder branches.
  - Instantiates `GoogleSheetPlanner` and prints quality summary.
- `local_run.py`
  - CLI wrapper and local event emulation.
- `index.py`
  - Cloud handler wrapper around `main`.

### application (mixed with infra)
- `core/planner.py`
  - Central orchestrator for sync/reminder/quality report flow.
  - Currently builds infra dependencies directly (`GoogleSheetsService`, OpenAI agent, Telegram reminder path).
- `core/manager.py`
  - Use-case orchestration around task update and calendar/table rendering.

### domain (mixed with infra)
- `core/contracts.py`
  - Row contracts and normalization helpers (mostly domain-safe).
- `core/errors.py`
  - Typed data-quality diagnostics (domain-safe).
- `core/repository.py`
  - Domain objects (`Task`, `TimingParser`) mixed with infrastructure reads/logging and repository implementation.
- `core/people.py`
  - Domain entity (`Person`) mixed with sheet-loading repository concerns.
- `core/reminder.py`
  - Reminder message generation/domain logic mixed with Telegram/OpenAI clients.

### infrastructure
- `utils/service.py`
  - Google Sheets/Drive API adapter and dry-run logging.
- `core/reminder.py::TelegramNotifier`
  - Telegram transport adapter.
- `core/reminder.py::AsyncOpenAIChatAgent`
  - OpenAI transport adapter.
- `config/*`
  - Environment/configuration loader and runtime constants.

## Active Cross-Layer Coupling (Observed)
- `main.py -> core/planner.py -> utils/service.GoogleSheetsService` (interfaces directly trigger infra construction).
- `core/planner.py -> core/reminder.AsyncOpenAIChatAgent/Reminder` (application directly instantiates infra chat adapter).
- `core/repository.py -> core/reminder.TelegramNotifier` (data parsing path depends on reminder transport module).
- `utils/service.py -> core/reminder.TelegramNotifier` (infra module depends on reminder module).
- `core/reminder.py` contains both message-domain logic and infra transports in one module.

## First Extraction Slice (Low Risk)

### Slice ID
`S2-SLICE-01`: isolate planner dependency construction boundary.

### Scope
- Introduce explicit dependency container/factory module (application boundary) used by `main.py`.
- Keep existing runtime behavior unchanged by preserving current implementations behind the same call flow.
- Do not move business logic yet; only separate construction wiring from planner orchestration.

### Candidate files
- `core/planner.py` (reduce constructor responsibility).
- `main.py` (switch to explicit dependency builder).
- New module candidate: `core/bootstrap.py` (or `application/bootstrap.py`) for wiring.

### Acceptance criteria
- `GoogleSheetPlanner` no longer directly creates all infra clients in constructor.
- Construction/wiring is isolated in a single bootstrap module.
- `local_run.py --mode sync-only --dry-run` and `local_run.py --mode reminders-only --dry-run --mock-external` stay green.

### Risks and controls
- Risk: hidden constructor side effects break run modes.
  - Control: keep backward-compatible defaults and smoke-check both sync and reminders flows.
- Risk: accidental behavior change in reminder flow.
  - Control: run reminder smoke with `--mock-external` and compare quality summary output.

## Notes
- This inventory intentionally reflects current mixed boundaries; it is a staging artifact for incremental extraction, not target architecture.
- 2026-02-27: `S2-SLICE-01` scaffold executed in DTM-20 (`core/bootstrap.py` + wiring through `main.py` and dependency injection in `core/planner.py`).

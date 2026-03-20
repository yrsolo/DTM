# Notes For Maintainers

## How to use this canon

- start every new architecture campaign from this folder
- treat `docs/architecture/runtime/*` as descriptive evidence
- treat `docs/architecture/recovery/*` as the previous recovery wave, not the current control doc set
- treat `docs/integrations/attachments/frontend-card-publication.md` as the governing concrete product scenario for publication/read-side work

## What to resist

- adding a bridge because it feels safer than deleting the old path
- polishing Telegram beyond reserve-capability needs
- calling a change "modular" when it only moves imports or adds wrappers
- letting browser-read shaping drift back into generic HTTP handlers

## Delta-audit expectation

Before the next code wave:
- verify current code against this canon
- record remaining top-path ambiguity
- record remaining bootstrap weight
- record any remaining fake-modularity or reserve-Telegram drift

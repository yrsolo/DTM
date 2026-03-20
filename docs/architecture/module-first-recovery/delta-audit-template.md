# Delta Audit Template

Use this template for the first execution wave under the module-first canon.

## Required table

| Scenario | Owning module | Current path | Target path | Status | Surviving old path | Fake-modularity risk | Next kill move | Required guardrail |
|---|---|---|---|---|---|---|---|---|
| example | access_api | entrypoint -> runtime -> wrapper -> old path | entrypoint -> runtime -> module | partial | old wrapper | medium | remove wrapper | import/readability guard |

## Status values

- `true`
- `partial`
- `violated`

## Required conclusions

- what is already consistent with the canon
- what still violates the canon
- which old path should die next
- which readability or fake-modularity regressions are most urgent

# Charter - CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1

## Why
- direct `/api` latency diagnostics showed contradictory numbers: `router_dispatch` and `http_shell` were much larger than `frontend_handler`
- before any optimization wave, direct `/api` traces must become internally consistent and decision-safe

## Goal
- make direct `/api` latency diagnostics trustworthy enough to localize time into:
  - router pre-check chain
  - actual selected handler call
  - post-router shell work
  - full function total
  - inner frontend handler total vs inner stage sum

## Non-goals
- no runtime speed optimization yet
- no `bff` work
- no frontend payload contract changes

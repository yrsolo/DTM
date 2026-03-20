# Bootstrap Discipline V2

This document defines bootstrap discipline for the active module-first runtime.

Governing source:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Active policy

- bootstrap remains the composition root
- bootstrap may delegate only
- new contexts may not be born through centralized ad-hoc wiring in a growing global bootstrap
- each new context must own its own `module.py`
- context-local builders may be lazy, but ownership must stay local to the context

## Practical rules

- bootstrap loads config and shared infrastructure dependencies
- bootstrap wires context entry builders only as needed
- bootstrap must not absorb business rules, route logic, or command-ownership logic
- bootstrap must not become the conceptual center of the codebase again

## Migration intent

- move bootstrap discipline earlier than the first full context extraction
- treat it as an enabling rule, not as a giant isolated reform campaign
- keep future context extraction reversible and locally owned

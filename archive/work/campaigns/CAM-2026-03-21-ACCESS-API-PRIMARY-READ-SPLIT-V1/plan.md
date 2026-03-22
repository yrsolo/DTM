# CAM-2026-03-21-ACCESS-API-PRIMARY-READ-SPLIT-V1

## Smell
- `PrimaryTaskListReadApi` still reads like a giant handler-shaped class that owns parsing, access resolution, snapshot query orchestration, masking, cache interaction, and response building in one place

## Target ideal
- `access_api` should expose a thin HTTP adapter over a module-owned primary read service
- HTTP path matching and response translation stay near the handler
- primary task-list orchestration moves into an application service with a calmer ownership story

## Kill criteria
- `PrimaryTaskListReadApi` becomes a thin HTTP adapter
- a new application-owned service executes the primary task-list read flow
- current HTTP behavior and tests remain unchanged

## Out of scope
- deep `snapshot` redesign
- `bootstrap` decomposition
- route changes or payload schema changes

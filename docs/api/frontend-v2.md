# Frontend API v2

## Purpose
Version 2 of frontend API adds a normalized, extensible contract:
- `meta`
- `filters`
- `summary`
- `entities`
- `tasks`

v1 stays available in parallel.

## Endpoints
- `GET /api/v2/frontend`
- `GET /api/v2/frontend/doc`
- `GET /api/v2/frontend/doc?format=json`

## Query Params
- `statuses`: comma-separated statuses, default `work,pre_done`
- `designer`: optional designer filter (case-insensitive exact member in multi-line field)
- `limit`: integer `1..1000`, default `200`
- `include_people`: bool (`1/0,true/false,yes/no`), default `true`

## Response Contract

### meta
- `artifact`: `dtm_frontend_api_v2`
- `contractVersion`: `2.0.0`
- `generatedAt`: UTC ISO datetime
- `syncedAt`: UTC ISO datetime
- `source`:
  - `env`
  - `sourceId`
  - `sheetName` (optional)
  - `sheetUrl` (optional)
- `hash`: stable payload hash (sha256 of stable JSON with `meta.hash=""`)
- `features`: capability map
- `paging`:
  - `limit`
  - `nextCursor`

### filters
Echo of requested filters.

### summary
Counts for returned task/entity sections.

### entities
- `people[]`: `id`, `name`, `position?`, `links`
- `groups[]`: `id`, `name`, `links`
- `tags[]`: reserved
- `enums`: status maps and status groups

### tasks
- `id`
- `title`
- `ownerId`
- `groupId`
- `status`
- `date`:
  - `start` (`YYYY-MM-DD|null`)
  - `end` (`YYYY-MM-DD|null`)
  - `nextDue` (`YYYY-MM-DD|null`)
- `tags[]`
- `hash` (`null` for now, reserved)
- `revision` (`null` for now, reserved)
- `links`:
  - `sheetRowUrl`
  - `self`

## ID Rules
- `task.id`: existing stable task id from source row.
- `person.id`: `Person.id` when present, otherwise deterministic hash from person name.
- `group.id`: deterministic hash from `task.project_name`.

## Examples

### Example 1: default query
```json
{
  "meta": {
    "artifact": "dtm_frontend_api_v2",
    "contractVersion": "2.0.0",
    "generatedAt": "2026-03-02T23:00:00Z",
    "syncedAt": "2026-03-02T23:00:00Z",
    "source": {"env": "test", "sourceId": "Спонсорские ТНТ", "sheetName": "Спонсорские ТНТ", "sheetUrl": null},
    "hash": "sha256...",
    "features": {"taskHash": true, "taskRevision": true, "entities": true},
    "paging": {"limit": 200, "nextCursor": null}
  },
  "filters": {"statuses": ["work", "pre_done"], "designer": "", "limit": 200, "includePeople": true},
  "summary": {"tasksReturned": 2, "peopleReturned": 2, "groupsReturned": 1},
  "entities": {"people": [], "groups": [], "tags": [], "enums": {"status": {}, "statusGroups": {}}},
  "tasks": []
}
```

### Example 2: designer filter
```json
{
  "filters": {"statuses": ["work"], "designer": "аня", "limit": 50, "includePeople": false},
  "summary": {"tasksReturned": 1, "peopleReturned": 0, "groupsReturned": 1}
}
```

### Example 3: task row shape
```json
{
  "id": "132",
  "title": "Бренд [Проект] Формат",
  "ownerId": "owner:unassigned",
  "groupId": "a18d5f82b13e01f0",
  "status": "work",
  "date": {"start": "2026-03-01", "end": "2026-03-09", "nextDue": "2026-03-04"},
  "tags": [],
  "hash": null,
  "revision": null,
  "links": {"sheetRowUrl": null, "self": "/api/v2/frontend/tasks/132"}
}
```

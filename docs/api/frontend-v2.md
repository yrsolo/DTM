# Frontend API v2 (Contract 2.0.1)

## Purpose
`v2` is the normalized frontend contract with default `milestones[]` and optional time-window filtering.

## Endpoints
- `GET /` -> v2 doc page (API root)
- `GET /api/v2/frontend`
- `GET /api/v2/frontend/doc`
- `GET /api/v2/frontend/doc?format=json`

## Query Params
- `statuses` (`string`, default `work,pre_done`): status filter list.
- `designer` (`string`, optional): case-insensitive designer filter.
- `limit` (`int`, default `200`, range `1..1000`).
- `include_people` (`bool`, default `true`).
- `window_start` (`YYYY-MM-DD`, optional).
- `window_end` (`YYYY-MM-DD`, optional).
- `window_mode` (`string`, default `intersects`, only supported value: `intersects`).

### Window Validation
- If one of `window_start/window_end` is missing and the second is set -> `400`.
- If dates are not `YYYY-MM-DD` -> `400`.
- If `window_start > window_end` -> `400`.
- Error shape:
```json
{
  "error": {
    "code": "invalid_window",
    "message": "...",
    "details": {}
  }
}
```

## Time Window Rule (`window_mode=intersects`)
Task is included if:
- `task.date.start` is inside `[window_start, window_end]` OR
- `task.date.end` is inside `[window_start, window_end]`.

If one of start/end is `null`, only the existing boundary is checked.
If both are `null`, task is excluded when window is enabled.

When window is disabled (default) no time filtering is applied.

## Response Shape
Top-level:
- `meta`
- `filters`
- `summary`
- `entities`
- `tasks`

## Field Implementation Status

### Implemented now
- `meta.*` including `hash`, `features.milestonesDefault`, `features.timeWindowFilter`.
- `filters.statuses`, `filters.designer`, `filters.limit`, `filters.include_people`, `filters.window`.
- `summary.tasksTotal`, `summary.tasksReturned`, `summary.peopleTotal`, `summary.groupsTotal`, `summary.milestonesTotal`.
- `entities.people[]`, `entities.groups[]`, `entities.enums.status`, `entities.enums.statusGroups`.
- `entities.enums.milestoneType` (dynamic, only used types from returned tasks).
- `entities.enums.milestoneStatus` (`planned|done|unknown|skipped`).
- `tasks[].id/title/ownerId/groupId/status/date/tags/links.self`.
- `tasks[].milestones[]` (always present; empty list if no milestones).
- `tasks[].milestones[].type/planned/actual/status`.

### Reserved / stubs
- `tasks[].hash` (currently `null`).
- `tasks[].revision` (currently `null`).
- `tasks[].links.sheetRowUrl` (currently `null`).
- `entities.tags[]` (currently empty).

## Milestones Rules
- `tasks[].milestones` is always present.
- Sort order: by `planned` asc (`null` goes last), then by `type`.
- If a task passes time-window filter, all its milestones are returned.

## Example (minimal)
```json
{
  "meta": {
    "artifact": "dtm_frontend_api_v2",
    "contractVersion": "2.0.1"
  },
  "filters": {
    "statuses": ["work", "pre_done"],
    "designer": null,
    "limit": 200,
    "include_people": true,
    "window": {"enabled": false, "start": null, "end": null, "mode": "intersects"}
  },
  "summary": {
    "tasksTotal": 0,
    "tasksReturned": 0,
    "peopleTotal": 0,
    "groupsTotal": 0,
    "milestonesTotal": 0
  },
  "entities": {
    "people": [],
    "groups": [],
    "tags": [],
    "enums": {
      "status": {},
      "statusGroups": {},
      "milestoneType": {},
      "milestoneStatus": {"planned": "Запланировано", "done": "Готово", "unknown": "Неизвестно", "skipped": "Пропущено"}
    }
  },
  "tasks": [
    {"id": "1", "milestones": []}
  ]
}
```

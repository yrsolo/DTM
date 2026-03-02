# Frontend API Contract

## Purpose
HTTP API surface for frontend data consumption from the running cloud function.

## Endpoints

### `GET /api/v1/frontend`
Main data endpoint.

Query params:
- `statuses`: optional CSV filter by `color_status`, default `work,pre_done`.
- `designer`: optional designer full-name filter (case-insensitive exact match against split names).
- `limit`: optional integer `1..1000`, default `200`.
- `include_people`: optional bool (`1/0`, `true/false`, `yes/no`), default `true`.

### `GET /api/v1/read-model`
Alias of `/api/v1/frontend`.

### `GET /api/v1/frontend/doc`
Returns machine-readable endpoint/response doc payload.

## Response shape (`/api/v1/frontend`)

Top-level fields:
- `artifact`: fixed `dtm_frontend_api_payload`
- `generated_at_utc`: UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`)
- `source`:
  - `env`: `dev|test|prod`
  - `source_sheet_name`
- `filters`: applied query filters
- `summary`:
  - `tasks_total`
  - `tasks_filtered`
  - `tasks_returned`
  - `people_total` (if `include_people=true`)
- `tasks`: array
- `deadlines`: nearest deadlines array
- `people`: array (if `include_people=true`)

Task item fields:
- `id`, `name`, `designer`, `status`, `color_status`
- `brand`, `format`, `project_name`, `customer`
- `min_date`, `max_date`, `next_due_date` (`YYYY-MM-DD` or `null`)
- `timing`: array of:
  - `date`: `YYYY-MM-DD`
  - `stages`: string array

Deadline item fields:
- `date`, `task_id`, `task_name`, `designer`, `stages`

People item fields:
- `id`, `name`, `position`, `vacation`, `telegram_id`, `chat_id`

## Errors
- Non-API paths continue existing behavior (planner/group-query/healthcheck flow).
- Runtime failures keep existing handler fallback body `!!!EGGORR!!!`.

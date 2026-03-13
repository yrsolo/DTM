# CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1

Status: planned
Priority: P0 after runtime/bootstrap and perf instrumentation foundation
Owner intent: add browser-facing auth integration and high-performance masked/full access without duplicating domain query logic.

## Source of truth for this campaign

Primary external handoff:
- `BACKEND_AUTH_HANDOFF.md`

Primary local principles:
- `docs/system/architecture_values.md`

## Problem statement

We need two browser-visible access modes:
- `full` — real data for authenticated approved users
- `masked` — same payload shape but sensitive text replaced with stable fake values

This must be:
- secure
- deterministic
- fast
- compatible with frontend contract
- implemented without splitting read-side business logic into two systems

## Browser-facing contract

### Route namespace

Prod:
- frontend: `https://dtm.solofarm.ru/`
- browser data path: `/ops/api/v2/frontend`
- auth/session path: `/ops/auth/*`

Test:
- frontend: `https://dtm.solofarm.ru/test/`
- browser data path: `/test/ops/api/v2/frontend`
- auth/session path: `/test/ops/auth/*`

Backend-owned reserved namespaces include:
- `/ops/api/*`
- `/ops/admin/*`
- `/ops/telegram*`
- `/test/ops/api/*`
- `/test/ops/admin/*`
- `/test/ops/telegram*`

## Security contract

Browser must never be trusted to set `x-dtm-*` auth headers.

Trusted headers from auth proxy/gateway chain:
- `x-dtm-access-mode: full | masked`
- `x-dtm-authenticated: 1 | 0`
- `x-dtm-contour: test | prod`
- `x-dtm-user-id`
- `x-dtm-user-role`
- `x-dtm-user-status`

Backend must treat these as trustworthy only through trusted ingress.

## Required design

### 1. AccessContext boundary object

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AccessContext:
    contour: str
    authenticated: bool
    access_mode: str
    user_id: str | None
    user_role: str | None
    user_status: str | None

    @property
    def allow_full(self) -> bool:
        return (
            self.authenticated
            and self.access_mode == "full"
            and self.user_status == "approved"
        )

    @property
    def require_masking(self) -> bool:
        return not self.allow_full
```

### 2. AccessContextResolver

```python
class AccessContextResolver:
    def from_http_event(self, event: dict) -> AccessContext: ...
```

### 3. One payload path only

Required pipeline:

`HTTP -> AccessContext -> canonical frontend payload build -> optional MaskingTransformer -> response`

Forbidden:
- separate masked query implementation
- masking inside query engine internals
- access branching scattered across domain services

### 4. Deterministic masking

Add configurable dictionary-backed pseudonymization.

Suggested structure:

```python
@dataclass(frozen=True)
class MaskingDictionaries:
    brands: tuple[str, ...]
    designers: tuple[str, ...]
    shows: tuple[str, ...]
    formats: tuple[str, ...]
    generic_words: tuple[str, ...]
    version: str
```

```python
class MaskingDictionaryProvider:
    def load(self) -> MaskingDictionaries: ...
```

```python
class StableMaskingMapper:
    def map_brand(self, real_value: str) -> str: ...
    def map_designer(self, real_value: str) -> str: ...
    def map_show(self, real_value: str) -> str: ...
    def map_format(self, real_value: str) -> str: ...
    def map_free_text(self, real_value: str) -> str: ...
```

### 5. Masking policy

```python
class MaskingPolicy:
    def should_mask_field(self, path: str, value: object) -> bool: ...
    def classify_field(self, path: str, value: object) -> str: ...
```

### 6. Transformer

```python
class MaskingTransformer:
    def transform(self, payload: dict, access: AccessContext) -> dict: ...
```

Transformer must preserve payload shape.

## What should remain stable in masked mode

Preserve as-is unless explicitly proven sensitive:
- ids
- dates
- statuses
- milestone order/sequence
- counters and meta structure
- frontend v2 payload shape

Mask sensitive display fields:
- task title
- brand
- customer
- show/group names
- designer/person names
- free-text comments/history/notes

## Performance requirements

1. Dictionaries must be loaded once per process or otherwise cached.
2. Masking must use deterministic pure mapping, not random generation.
3. Hot path must expose metrics for:
   - access context resolve
   - payload build
   - masking transform
   - total response
4. Consider optional prebuilt hot cache for default frontend request in both full and masked modes.

## Suggested file placement

### Core access boundary
- `src/entrypoints/http/access_context.py`
- `src/entrypoints/http/access_context_resolver.py`

### Masking implementation
- `src/services/access/masking_policy.py`
- `src/services/access/masking_dictionaries.py`
- `src/services/access/masking_mapper.py`
- `src/services/access/masking_transformer.py`

### Frontend use-case seam
- `src/services/frontend_v2_usecase.py`

### Optional hot cache
- `src/services/frontend_hot_cache.py`

## Concrete tasks

1. Introduce reserved browser-facing `/ops/*` and `/test/ops/*` route handling.
2. Add `AccessContextResolver` based on trusted proxy headers.
3. Refactor frontend v2 path to one canonical payload build seam.
4. Add deterministic masking dictionaries and mapper.
5. Add masking transformer with shape-preserving behavior.
6. Add tests for:
   - full vs masked same shape
   - deterministic mapping stability
   - trusted-header behavior
   - anonymous request -> masked
   - authenticated approved full request -> full
7. Add stage metrics for access resolve/build/masking.
8. Optionally add default hot cache for masked/full frontend payload.

## Acceptance criteria

- frontend contract matches handoff namespace
- masked and full share one payload contract
- sensitive fields are masked deterministically
- backend does not trust browser-auth headers outside trusted path
- masked path is fast enough and separately timed

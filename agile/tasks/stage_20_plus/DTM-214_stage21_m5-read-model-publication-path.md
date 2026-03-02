# DTM-214: Stage 21 M5 read-model publication path

## Context
- M5 requires not only builder logic but also artifact publication path for downstream consumers.
- Build handler still had placeholder implementation.

## Goal
- Add file-based read-model publisher service.
- Wire `src/handlers/build_readmodels.py` to:
  - build read-model payload
  - optionally publish to file
- Add tests for publisher and handler.

## Non-goals
- No Object Storage publication in this task.
- No production runtime entrypoint switch.

## Plan
1. Add `publish_read_model_to_file`.
2. Wire build-readmodels handler.
3. Add unit tests.

## Checklist (DoD)
- [x] Publisher helper committed.
- [x] Build-readmodels handler now functional.
- [x] Tests for publisher + handler pass.

## Work log
- 2026-03-02: Added `src/services/readmodels/publisher.py`.
- 2026-03-02: Updated `src/handlers/build_readmodels.py` to build/publish payload.
- 2026-03-02: Added tests for publisher and handler.

## Links
- `src/services/readmodels/publisher.py`
- `src/handlers/build_readmodels.py`
- `tests/services/test_readmodel_publisher.py`
- `tests/handlers/test_build_readmodels_handler.py`

# Stage 12 Code Quality Standard

## Scope
Applies to all Python modules touched in Stage 12.

## Mandatory Rules
1. Type hints:
   - public functions/methods must have parameter and return types;
   - avoid ambiguous `Any` unless justified.
2. Docstrings:
   - keep concise, intent-focused, and aligned with actual behavior;
   - remove stale/duplicated descriptions.
3. Naming:
   - explicit names over abbreviations;
   - avoid mixed language within identifiers.
4. Readability:
   - split oversized methods by intent;
   - remove dead branches and obsolete comments.
5. Logging/errors:
   - consistent error phrasing and context fields;
   - no secret values in logs.

## Audit Template (per method)
- Purpose clear: yes/no
- Side effects explicit: yes/no
- Typing complete: yes/no
- Docstring accurate: yes/no
- Complexity acceptable: yes/no
- Notes / required fix:

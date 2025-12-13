# Task 003: Remove Heuristic Name-Matching in PostgreSQL Writes; Use Stable IDs

## Goal
Eliminate unreliable Postgres mapping such as `project_code.replace('-', ' ')` and name-based heuristics. Replace it with stable identifiers for projects/features/specs/tasks.

## Context (from audit)
- Postgres mapping currently uses heuristics (dangerous in multi-project DBs).
- Tasks use `metadata->>'code'`, but projects/features/specs rely on name matching.
- This can mis-link records and corrupt data associations.

## Scope
- Introduce a stable identifier strategy for Postgres writes:
  - Prefer explicit `code` columns if they exist.
  - If schema cannot be changed, store `code` in `metadata` for *all* entities and query by it.

## Dependencies
- Task 002 (schema contract alignment) should inform the identifier strategy.

## Files likely involved
- `src/services/data_store_gateway.py` (Postgres branch)
- `src/services/matchers/*` (if relying on name)
- Tests that verify linking behavior

## Steps
1. Identify every place Postgres logic looks up entities by name heuristics.
2. Define a single rule for identifiers (e.g., `metadata->>'code'` everywhere).
3. Update create/update logic to:
   - upsert by stable identifier
   - return IDs from the database and use them for relationships
4. Remove compatibility/workaround branches that are explicitly “dangerous for real use”.
5. Add/extend tests:
   - multi-project scenario (2 projects with similar names/codes)
   - verify features/specs/tasks link to the correct project

## Acceptance criteria
- No Postgres write path depends on name normalization heuristics.
- Relationships are established using stable IDs (or stable code keys) and cannot silently link to the wrong project.
- Tests cover at least one case where heuristics would previously mis-link.

## Non-goals
- Splitting the gateway into separate modules (handled in a later refactor task).

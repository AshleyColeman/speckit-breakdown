# Task 002: Align PostgreSQL Read Methods With Actual Schema (and Tests)

## Goal
Make PostgreSQL read/query methods consistent with the actual schema used in integration tests, eliminating contradictory assumptions (e.g., `code` vs `name`).

## Context (from audit)
- `get_project()` returns `None`.
- `get_feature()` / `get_spec()` Postgres queries appear to assume `features.code`, `specs.code`, etc.
- Integration test verifies via `features WHERE name = 'Test Feature'` and `specs WHERE name = 'Test Spec'`.

## Scope
- Decide the authoritative Postgres schema contract for projects/features/specs/tasks.
- Update Postgres getters to match that contract.
- Update tests if the intended contract differs.

## Dependencies
- Task 001 (Postgres gating) can land first to reduce risk while this work is in progress.

## Files likely involved
- `src/services/data_store_gateway.py`
- `tests/integration/test_cli_db_prepare_postgres.py`
- Any schema docs (if added)

## Steps
1. [x] Inspect integration tests to determine what the database schema is expected to look like (columns, names, metadata usage).
2. [x] Inspect the Postgres SQL in gateway methods:
   - `get_project`, `get_feature`, `get_spec`, `get_task` (and any matchers calling them)
3. [x] Choose the contract:
   - Either: `name` is canonical
   - Or: `code` is canonical (and tests should be updated)
4. [x] Update Postgres read methods to query by canonical identifiers.
5. [x] Ensure read methods return complete, consistent objects used by matchers/orchestrator.
6. [x] Add coverage:
   - Minimal unit/integration tests that verify reads succeed after writes.

## Acceptance criteria
- Postgres integration tests pass without relying on contradictory assumptions.
- `EntityMatcher.find_existing_*` works for Postgres (no `None` stubs).
- Read methods behave deterministically (no heuristic mapping).

## Non-goals
- Full Postgres refactor (handled later).

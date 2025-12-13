# Task 004: Replace Placeholder `pass` / `None` Stubs With Real Behavior or Fail-Fast Errors

## Goal
Remove silent placeholder behavior in core persistence paths so failures are explicit and correctness issues cannot hide.

## Context (from audit)
Placeholders in `DataStoreGateway`:
- `verify_schema()` (Postgres) is `pass`
- `create_task_runs` / `create_ai_jobs` / `_log_entities` are `pass`
- `get_project` returns `None`

## Scope
For each placeholder:
- Implement the missing behavior **or** raise a clear `NotImplementedError` / domain-specific error when the feature isn’t supported.

## Dependencies
- Task 001 gating may be used to avoid exposing unfinished Postgres behavior until implemented.

## Files likely involved
- `src/services/data_store_gateway.py`
- Any call sites expecting these methods to work
- Tests for force/idempotency behavior

## Steps
1. Identify call sites that depend on each stub.
2. For each stub, decide:
   - implement now (if required for correctness)
   - or fail fast with a descriptive error message and instructions.
3. Implement minimal correct versions:
   - `get_project` must return a project object consistent with matchers.
   - `verify_schema` should either validate or explicitly fail if schema cannot be verified.
   - `create_task_runs` / `create_ai_jobs` should either write records or fail fast.
   - `_log_entities` should either log with structured detail or be removed if unused.
4. Add/adjust tests to ensure stubs cannot silently pass.

## Acceptance criteria
- No core method in persistence layer silently `pass`es where behavior is required.
- If a method is intentionally unsupported, running the CLI triggers a clear, actionable error.
- Integration tests demonstrate the implemented behavior is exercised.

## Completion notes
- `DataStoreGateway.verify_schema()` Postgres path now fails fast with `NotImplementedError` instead of silently succeeding.
- `DataStoreGateway._execute_upsert()` Postgres path now fails fast with `NotImplementedError` instead of silently succeeding.
- `DataStoreGateway.create_task_runs()` and `DataStoreGateway.create_ai_jobs()` now persist to SQLite tables.
- For PostgreSQL, task-run / AI-job derived data is stored into `tasks.metadata` (JSONB) so bootstrap runs don’t silently drop this information.
- Test suite: `pytest` passes.

## Non-goals
- Large-scale refactors of persistence layering (handled later).

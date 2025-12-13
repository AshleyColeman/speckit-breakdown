# Task 006: Enable SQLite Foreign Keys + Strengthen SQLite Schema Safety

## Goal
Improve SQLite data integrity by enforcing foreign keys and tightening schema constraints where feasible.

## Context (from audit)
- SQLite schema is auto-created.
- FK constraints may not be enforced unless `PRAGMA foreign_keys=ON` is set.

## Scope
- Ensure every SQLite connection enables foreign key enforcement.
- Optionally strengthen schema constraints (unique keys, NOT NULL) if compatible with existing behavior.

## Files likely involved
- `src/services/data_store_gateway.py` (SQLite connection setup + schema creation)
- Any helper functions that open SQLite connections
- Integration tests around idempotency/force mode

## Steps
1. Identify all SQLite connection creation points.
2. Execute `PRAGMA foreign_keys=ON` on every SQLite connection.
3. Add a test that demonstrates FK enforcement:
   - inserting a dependency referencing a non-existent task should fail.
4. Review schema creation and consider tightening:
   - `tasks(code)` uniqueness
   - FKs `ON DELETE` behavior if appropriate
5. Ensure changes do not break existing integration tests.

## Acceptance criteria
- SQLite foreign key enforcement is enabled for all SQLite operations.
- A test proves FK constraints are active.
- Existing CLI/db.prepare tests continue to pass.

## Non-goals
- Introducing migrations tooling (handled separately if needed).

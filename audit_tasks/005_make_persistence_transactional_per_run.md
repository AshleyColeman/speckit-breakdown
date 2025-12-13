# Task 005: Make Persistence Transactional Per Run (SQLite + PostgreSQL)

## Goal
Ensure a db.prepare “run” is atomic so partial writes cannot leave the database in an inconsistent state.

## Context (from audit)
- Orchestrator persists entities, then dependencies, then task_runs, then ai_jobs.
- There is no transaction spanning these steps.

## Scope
- SQLite: single transaction for the full persistence phase.
- Postgres: single connection + single transaction for the full persistence phase.

## Dependencies
- Task 004 (stubs) should be resolved or fail fast; transactional correctness depends on complete behavior.

## Files likely involved
- `src/services/bootstrap_orchestrator.py`
- `src/services/data_store_gateway.py` (or new gateway modules)

## Steps
1. Identify the full “write unit” performed during a single orchestrator run.
2. Add an explicit transaction boundary around the full persistence phase.
   - SQLite: `BEGIN`/`COMMIT` with rollback on exception.
   - Postgres: `conn.autocommit = False` and `conn.commit()`/`conn.rollback()`.
3. Ensure every write method uses the same connection/transaction context.
4. Add tests:
   - simulate a failure mid-run and verify no partial data remains.

## Acceptance criteria
- On any exception during persistence, the database is rolled back to the pre-run state.
- Integration tests cover rollback behavior for SQLite at minimum.
- Postgres path uses one connection per run (not per method inside loops) within the transaction.

## Non-goals
- Performance optimizations beyond what is needed to support transaction scoping (handled later).

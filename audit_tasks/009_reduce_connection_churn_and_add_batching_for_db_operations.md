# Task 009: Reduce DB Connection Churn + Add Batching Where Safe

## Goal
Improve performance and reliability by reusing connections and reducing per-entity connection opens, especially for PostgreSQL.

## Context (from audit)
- Postgres code opens new connections inside loops in some methods.
- SQLite uses per-method connections and minimal batching.

## Scope
- Ensure one Postgres connection per run (and per transaction, see Task 005).
- Add batching for repetitive inserts/upserts where safe.

## Dependencies
- Task 005 (transaction-per-run) should either be complete or integrated with this.

## Files likely involved
- `src/services/data_store_gateway.py` (or split gateways from Task 008)

## Steps
1. Identify all loops doing `connect()` repeatedly.
2. Refactor to pass a shared connection/cursor context through write operations.
3. Where appropriate, batch writes:
   - use `executemany` (SQLite) / `execute_batch` or `executemany` (psycopg2) as applicable.
4. Add a regression test or benchmark-style test (lightweight) asserting connection count is not proportional to entity count.

## Acceptance criteria
- Postgres path opens a single connection per run for persistence operations.
- Performance improves for large numbers of tasks/features.
- No behavior regressions in integration tests.

## Non-goals
- Large schema changes.

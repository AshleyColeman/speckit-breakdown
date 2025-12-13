# Task 008: Split `DataStoreGateway` Into Protocol + Backend Implementations

## Goal
Reduce coupling and “god-file” risk by separating SQLite and Postgres implementations behind a stable interface.

## Context (from audit)
- `src/services/data_store_gateway.py` is large and mixes schema creation, read/write logic, retry behavior, and sqlite/postgres branching.

## Scope
- Introduce a storage interface/protocol describing methods the orchestrator depends on.
- Implement `SqliteGateway` and `PostgresGateway` as separate modules.
- Keep orchestrator call sites stable (dependency injection only).

## Dependencies
- Safer after Tasks 002–007 clarify correct Postgres behavior.

## Files likely involved
- `src/services/data_store_gateway.py`
- `src/services/bootstrap_orchestrator.py`
- `src/services/upsert_service.py`
- Any gateway factory/selection logic

## Steps
1. Identify the minimal set of gateway methods used by orchestrator/upsert.
2. Define a `Protocol` (or abstract base class) with those methods.
3. Extract SQLite code into `sqlite_gateway.py`.
4. Extract Postgres code into `postgres_gateway.py`.
5. Keep a thin compatibility shim if needed (temporary) that selects the backend.
6. Update tests to import/use the new structure.

## Acceptance criteria
- Orchestrator works unchanged except for gateway construction/injection.
- No runtime behavior changes beyond the refactor.
- File size of the old god-file is substantially reduced.

## Non-goals
- Functional changes to Postgres correctness beyond what’s needed to keep behavior consistent.

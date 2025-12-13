# Task 007: Implement PostgreSQL `verify_schema()` (or Fail Fast With Clear Contract)

## Goal
Prevent silent schema drift by validating the PostgreSQL schema contract at runtime, or failing fast with explicit instructions.

## Context (from audit)
- Postgres `verify_schema()` is currently `pass`.
- Postgres behavior is schema-assumption heavy.

## Scope
- Implement `verify_schema()` for Postgres.
- Validate required tables/columns and required semantics (e.g., `metadata->>'code'` usage if that’s the contract).

## Dependencies
- Informed by Task 002 (schema alignment) and Task 003 (stable identifiers).

## Files likely involved
- `src/services/data_store_gateway.py`
- Postgres integration tests

## Steps
1. Define the minimal Postgres schema contract required by this repo.
2. In `verify_schema()`:
   - check tables exist
   - check required columns exist
   - check required JSON fields are queryable if relied upon
3. If schema mismatch:
   - raise a descriptive error explaining what’s missing and how to fix it
4. Add tests:
   - one passing case against expected schema
   - one failing case (can be unit-level with mocks) that asserts the error message is actionable

## Acceptance criteria
- Postgres runs either validate schema successfully or fail before any writes.
- Error messages describe required tables/columns and expected identifier rules.
- No silent `pass` remains for Postgres schema verification.

## Non-goals
- Providing migrations tooling (can be done later).

## Status
- [x] Done

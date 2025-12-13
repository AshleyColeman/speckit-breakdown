# Task 001: Define Support Tier + Gate PostgreSQL Usage

## Goal
Prevent accidental “production” usage of PostgreSQL until the implementation is made correct, and make the support level explicit in docs and runtime.

## Context (from audit)
- PostgreSQL support is described as not production-grade.
- Current behavior can perform heuristic name-matching and “dangerous for real use” workarounds.
- This creates data integrity risk and confusing failures.

## Scope
- Add an explicit **support tier** statement (SQLite stable; PostgreSQL experimental/disabled-by-default).
- Add a **runtime guard** so PostgreSQL cannot be used unless explicitly enabled.

## Proposed approach
- Add a CLI flag (or config flag) such as `--enable-experimental-postgres`.
- If `--db-url` is PostgreSQL and the flag is not set:
  - fail fast with a clear error message.
  - include a link/reference to docs describing support tiers.

## Files likely involved
- `src/cli/commands/db_prepare.py`
- `src/lib/config_loader.py` (if config-driven)
- `README.md` (support matrix)
- Any Postgres connection / gateway selection logic

## Steps
1. [x] Identify where `--db-url` is parsed and where gateway selection occurs.
2. [x] Introduce a boolean gate (flag/config) defaulting to `False`.
3. [x] Add a fail-fast check when Postgres is selected and gate is `False`.
4. [x] Update user-facing docs:
   - Support Matrix section (SQLite stable, Postgres experimental)
   - Safe usage guidance
5. [x] Add/adjust tests:
   - When Postgres URL used without gate: command exits non-zero + message contains “experimental” / “enable flag”.
   - When gate enabled: behavior proceeds.

## Acceptance criteria
- Running db prepare with a `postgresql://...` URL without the explicit gate fails with a clear, actionable message.
- Docs clearly state support tiers.
- Tests cover both gated and allowed paths.

## Non-goals
- Making Postgres correct (handled by later tasks).

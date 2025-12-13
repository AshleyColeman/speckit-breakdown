# Task 014: Update Docs (Support Matrix + Python CLI Usage)

## Goal
Align documentation with reality: clarify what is supported, how to run the Python CLI locally, and what database schemas are expected.

## Context (from audit)
- README focuses on workflows/installation, not Python CLI usage.
- Docs claim “transactional safety” and rollback integration that aren’t present.
- Postgres schema contract is missing.

## Scope
- Add Support Matrix section: SQLite stable; Postgres experimental (or disabled by default).
- Add “Python CLI” quickstart:
  - install deps
  - run `src/cli/main.py`
  - run `/speckit.db.prepare`
- Add a short statement of schema expectations for SQLite and Postgres.
- Remove or correct claims about rollback/transactionality if not implemented.

## Files likely involved
- `README.md`
- `docs/speckit_system_guide.md` (or relevant docs)

## Steps
1. Identify doc sections that overpromise (rollback/transactional safety).
2. Update docs to match actual behavior after Tasks 005/007.
3. Add Support Matrix and Python CLI usage instructions.
4. Add a short Postgres schema contract section or link to where it’s defined.

## Acceptance criteria
- Docs match runtime behavior.
- A new developer can follow docs to run the CLI.
- Support tiers are explicit and consistent.

## Non-goals
- Implementing missing runtime behavior (handled in other tasks).

# Task 020: Integrate (or Remove) Unused Safety Mechanisms: Locking + Rollback/Guards

## Goal
Eliminate “architecture drift” by either implementing the safety mechanisms claimed by docs (locking/rollback/resource guards) or removing the dead/unused code paths and updating docs.

## Context (from audit)
- Docs claim rollback safety and validations, but orchestrator does not use `RollbackManager` across a run.
- File locking and resource guard utilities appear unused.
- Risk: “works in tests” but fails in real usage and is hard to debug.

## Scope
- Determine which mechanisms are intended to be part of the supported product:
  - file locking to prevent concurrent runs
  - rollback manager / transactional safety across steps
  - resource guard (if present)
- Either wire them into the execution path or delete/retire them and update docs.

## Dependencies
- Task 005 (transaction per run) may overlap with rollback/atomicity. Decide the layering (DB transaction vs rollback manager).

## Files likely involved
- `src/services/bootstrap_orchestrator.py`
- `src/lib/locking.py`
- `src/lib/rollback_manager.py` (if present)
- `src/lib/resource_guard.py` (if present)
- Docs that mention rollback/guards

## Steps
1. Identify the current intended concurrency model:
   - Can `db.prepare` run concurrently on the same project?
2. If concurrency should be prevented:
   - integrate `locking` at the CLI entrypoint or orchestrator start.
3. Decide on rollback strategy:
   - If DB transactions (Task 005) provide atomicity, document that and remove redundant rollback manager usage.
   - If rollback manager is intended for filesystem side-effects, define what it covers and integrate it.
4. Ensure errors are reported clearly when a lock cannot be acquired or rollback occurs.
5. Add tests:
   - lock prevents concurrent runs
   - rollback behavior is triggered on simulated failure (DB and/or filesystem)

## Acceptance criteria
- There are no “claimed” safety mechanisms that are silently unused.
- Either:
  - locking/rollback/guards are actually active and tested, or
  - they are removed and docs updated so expectations match reality.

## Non-goals
- Building a full distributed locking system.

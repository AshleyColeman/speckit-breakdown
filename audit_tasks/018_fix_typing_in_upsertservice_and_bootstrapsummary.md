# Task 018: Improve Typing Clarity in `UpsertService` and `BootstrapSummary`

## Goal
Increase refactor safety by removing intentionally vague typing in core orchestration/persistence boundaries.

## Context (from audit)
- `UpsertService.__init__(..., gateway: object)` untyped.
- `BootstrapSummary.validation_result: Optional[object]` loses type safety.

## Scope
- Type the gateway dependency with a protocol/interface (pairs well with Task 008).
- Introduce explicit type(s) for validation results.

## Files likely involved
- `src/services/upsert_service.py`
- `src/services/bootstrap_orchestrator.py` (or summary model)
- `src/models/entities.py` (if types live here)

## Dependencies
- Easier after Task 008 defines a gateway interface.

## Steps
1. Define a `Protocol` for the gateway methods UpsertService uses.
2. Update `UpsertService` signatures to use the protocol.
3. Replace `Optional[object]` with a typed validation result model or union.
4. Ensure mypy/type checking (if used) remains satisfied, or add minimal type validation in tests.

## Acceptance criteria
- `gateway` is no longer typed as `object`.
- `validation_result` has an explicit type.
- No runtime behavior changes.

## Non-goals
- Introducing a full static type-checking pipeline if one doesn’t exist.

# Task 017: Tighten Validation + Fail Fast on Safety-Critical Parse Errors

## Goal
Make validation safety-critical by reducing “log and continue” patterns and resolving uncertainty/mismatches in validation rules.

## Context (from audit)
- Validation includes self-noted uncertainty and mismatched attribute commentary (e.g., `DuplicateEntityRule`).
- Parsers often do `except Exception: logger.error(...); continue`, which can hide invalid inputs.

## Scope
- Identify parse/validation errors that must stop the run.
- Make persistence strict: required fields must exist.
- Clean up validation rule intent and typing.

## Files likely involved
- `src/services/validation/rules.py`
- Parser modules under `src/services/parser/`
- Orchestrator error handling

## Steps
1. Review validation rules for “TODO/uncertain” comments or mismatches.
2. Define which errors are fatal (e.g., missing codes, duplicate identifiers, invalid dependencies).
3. Update parser/orchestrator to fail fast on fatal errors.
4. Add unit tests for validation rules.
5. Add integration tests for fatal error behavior.

## Acceptance criteria
- Fatal input errors stop execution with a clear message.
- Validation rules match actual entity model fields.
- Tests cover key validation guarantees.

## Non-goals
- Redesigning the entire validation framework.

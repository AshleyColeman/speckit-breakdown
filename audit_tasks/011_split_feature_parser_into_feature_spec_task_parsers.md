# Task 011: Split `feature_parser.py` Into Smaller Parsers

## Goal
Reduce complexity and improve testability by splitting the oversized parser into focused modules.

## Context (from audit)
- `src/services/parser/feature_parser.py` is ~600 lines and contains Feature/Spec/Task parsing.

## Scope
- Incrementally split into:
  - `feature_parser.py` (feature-level orchestration)
  - `spec_parser.py`
  - `task_parser.py`
- Keep public APIs and imports stable (or update call sites carefully).

## Files likely involved
- `src/services/parser/feature_parser.py`
- `src/services/parser/*`
- Parser tests (if any)

## Steps
1. Identify logical boundaries between feature/spec/task parsing.
2. Extract code into new modules while keeping existing entry points stable.
3. Add focused unit tests for each parser.
4. Ensure integration tests still pass.

## Acceptance criteria
- `feature_parser.py` is significantly smaller and delegates to spec/task parsers.
- Tests exist for each parser module.
- No behavior regressions.

## Non-goals
- Changing parsing semantics (unless required for correctness).

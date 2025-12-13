# Task 019: Align `AGENT.md` “Hard Rules” With Reality (or Enforce Them)

## Goal
Remove ongoing friction by either enforcing file/function size limits or updating the rules to match the real codebase.

## Context (from audit)
- Repo hard rules claim max 500 lines per file and 40 lines per function.
- Several files exceed these limits.

## Scope
Choose one:
- Option A: Enforce rules
  - refactor oversized files/functions to comply.
  - add CI checks.
- Option B: Update rules
  - revise `AGENT.md` to reflect current constraints and a realistic roadmap.

## Files likely involved
- `AGENT.md`
- Oversized files:
  - `src/services/data_store_gateway.py`
  - `src/services/bootstrap_orchestrator.py`
  - `src/services/parser/feature_parser.py`

## Steps
1. Decide whether limits are aspirational or enforced.
2. Implement Option A or B.
3. If enforcing, add CI lint/check step.

## Acceptance criteria
- Repo guidance matches actual enforcement.
- Contributors have a clear standard that won’t cause churn.

## Non-goals
- Aesthetic refactors unrelated to maintainability.

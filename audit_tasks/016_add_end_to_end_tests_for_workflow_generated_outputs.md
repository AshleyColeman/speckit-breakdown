# Task 016: Add End-to-End Tests for Workflow Output Schema

## Goal
Improve confidence in the primary product surface (Markdown workflows) by validating generated outputs, not just script execution.

## Context (from audit)
- Workflows instruct agents to write files directly.
- Repo does not validate generated outputs or enforce a schema.
- Bats tests exist for installer; extend coverage to outputs.

## Scope
- Add fixture “real project” inputs.
- Run breakdown workflow (or equivalent generation path).
- Validate outputs against a defined schema/structure.

## Files likely involved
- `tests/bash/*`
- `tests/fixtures/projects/*`
- Potentially Python validators if used

## Steps
1. Identify which workflow outputs are considered “contract” (files/paths/frontmatter keys).
2. Define a schema checklist (could be JSON schema-like rules, or custom assertions).
3. Add an E2E test that:
   - runs the workflow on a fixture
   - verifies output files exist
   - verifies required fields/sections are present
4. Ensure the test is stable and not environment-dependent.

## Acceptance criteria
- E2E test fails if workflow output is missing required structure.
- E2E test runs in CI.

## Non-goals
- Testing every possible workflow branch.

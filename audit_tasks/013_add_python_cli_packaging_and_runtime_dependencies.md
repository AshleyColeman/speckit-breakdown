# Task 013: Add Proper Python CLI Packaging + Runtime Dependencies

## Goal
Make the Python CLI subsystem installable and reproducible with pinned runtime dependencies.

## Context (from audit)
- No `pyproject.toml`.
- `requirements.txt` appears to include test dependencies only.
- This will become painful as more CLI commands are added.

## Scope
- Establish a clear packaging/dependency strategy for runtime vs dev/test deps.
- Ensure a new dev can install and run the CLI deterministically.

## Files likely involved
- `requirements.txt`
- (Optionally) add `pyproject.toml`
- README developer instructions
- CI workflow if needed

## Steps
1. Identify actual runtime imports used by `src/cli/main.py` and services (e.g., `psycopg2`, YAML parsing choice from Task 012).
2. Decide packaging strategy:
   - Minimal: split `requirements.txt` into runtime + dev requirements.
   - Better: add `pyproject.toml` and use extras for dev/test.
3. Pin versions appropriately.
4. Update CI to install runtime + dev deps as needed.
5. Add a brief “Python CLI” section in README (see Task 014 for docs content; keep this task focused on packaging mechanics).

## Acceptance criteria
- Fresh environment can install dependencies and run CLI.
- CI uses the same dependency declaration.
- Runtime dependencies are explicit (no hidden global deps).

## Non-goals
- Publishing to PyPI.

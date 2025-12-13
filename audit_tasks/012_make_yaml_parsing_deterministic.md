# Task 012: Make YAML Parsing Deterministic (Add PyYAML or Remove YAML Support)

## Goal
Ensure YAML/frontmatter parsing behaves the same on every machine by removing implicit dependency on globally installed packages.

## Context (from audit)
- Parsers attempt `import yaml` (PyYAML) but `requirements.txt` does not include PyYAML.
- Fallback parser is more permissive; behavior changes across environments.

## Scope
Choose one:
- Option A: Add `PyYAML` as an explicit runtime dependency and use it consistently.
- Option B: Remove YAML parsing and standardize on the simple parser (document the limitation).

## Files likely involved
- Parser modules that handle YAML/frontmatter
- `requirements.txt` (and/or packaging changes)
- Docs describing supported frontmatter format

## Steps
1. Find all YAML/frontmatter parsing entry points.
2. Implement chosen option (A or B).
3. Add tests that assert identical parsing behavior regardless of environment.
4. Update docs to match supported formats.

## Acceptance criteria
- Parsing behavior does not depend on whether PyYAML happens to be installed.
- Tests cover frontmatter parsing determinism.

## Non-goals
- Supporting arbitrary YAML features beyond what the project needs.

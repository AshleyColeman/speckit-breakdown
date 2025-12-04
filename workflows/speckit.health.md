---
description: Run a SpecKit health check and summarise the results for a project or feature.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

User input may optionally specify:
- `scope: project` or `scope: feature:<id>`.

## Outline

1. **Prerequisite check**
   - From repo root, run:
     - `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks --require-advanced`
   - Use the JSON output to confirm feature paths.

2. **Run health-check script**
   - From repo root, run:
     - `.specify/scripts/bash/health-check.sh --json [--scope=project|feature]`
   - Capture the JSON output on stdout (same structure as `.speckit/health/report.json`).
   - Note the script's exit code:
     - `0` = healthy / informational
     - `1` = warnings
     - `2` = critical issues

3. **Generate rich markdown report with speckit.health prompt**
   - Read `.speckit/health/report.json`.
   - Use `.claude/commands/speckit.health.md` as guidance to produce a readable markdown report.
   - Overwrite `.speckit/health/report.md` with the improved report.

4. **Report**
   - Surface a concise summary to the user:
     - Overall status
     - Issue counts by severity
     - Pointers to `report.json` and `report.md`.

## Notes

- This workflow is safe and non-destructive. It only reads design artifacts and writes to `.speckit/health/`.
- It is intended to be idempotent; re-running will update the health snapshot to reflect current repo state.

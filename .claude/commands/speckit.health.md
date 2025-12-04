---
description: Generate a health report for a SpecKit project or feature from a JSON health summary.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

User input may optionally include:
- `scope: project` or `scope: feature:<id>`
- Any notes about which types of issues to emphasise (e.g., "focus on missing tasks").

## Outline

1. **Load health summary JSON**
   - Assume the shell workflow has already run:
     - `.specify/scripts/bash/health-check.sh --json [--scope=project|feature]`
   - That script writes:
     - `.speckit/health/report.json` (machine-readable summary)
     - `.speckit/health/report.md` (basic markdown summary)
   - Read and parse `.speckit/health/report.json` as the **source of truth**:
     - Top-level fields: `id`, `projectName`, `scope`, `featureId`, `generatedAt`, `status`.
     - `issues[]`: each with `issueId`, `severity`, `message`, `file`, `suggestion`.

2. **Produce a readable markdown health report**
   - Generate a richer markdown document that:
     - Clearly states overall status: `healthy`, `warning`, or `critical`.
     - Groups issues by severity (`critical`, `warning`, `info`).
     - Highlights the most important blockers first.
     - Points back to relevant files and suggested next actions.
   - Provide sections such as:
     - Summary
     - Status and key indicators
     - Critical issues
     - Warnings
     - Informational notes
     - Recommended next steps (with `/speckit.*` commands where appropriate).

3. **Write updated markdown report**
   - Use `write_to_file` to overwrite `.speckit/health/report.md` with the improved version.
   - Preserve the core facts from `report.json`; do NOT contradict them.

4. **Report back**
   - Return a short summary including:
     - Overall status
     - Count of issues by severity
     - Path to the updated markdown report.

## Health Report Structure (Guideline)

When generating `.speckit/health/report.md`, prefer a structure like:

```markdown
# SpecKit Health Report: [project or feature]

**Scope**: [project|feature <id>]
**Status**: [healthy|warning|critical]
**Generated At**: [timestamp]

## 1. Summary
- [One–three bullets summarising health]

## 2. Status & Indicators
- Overall status: **[status]**
- Critical issues: [N]
- Warnings: [N]
- Informational: [N]

## 3. Critical Issues
- [issueId] – [message] (file: `path`)
  - Suggested action: [suggestion]

## 4. Warnings
- [issueId] – [message] (file: `path`)
  - Suggested action: [suggestion]

## 5. Informational Notes
- [issueId] – [message]

## 6. Recommended Next Steps
- [List concrete `/speckit.*` commands or edits to run next]
```

Always align issue content with the underlying JSON; if something is unclear or missing, call it out explicitly rather than guessing.

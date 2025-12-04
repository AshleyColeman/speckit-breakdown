---
description: Build a SpecKit context pack under .speckit/context for use by AI agents and automation.
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
   - Parse the JSON output to obtain absolute paths for:
     - `REPO_ROOT`, `FEATURE_DIR`, `FEATURE_SPEC`, `IMPL_PLAN`, `TASKS`.

2. **Determine scope**
   - Default scope: `feature`.
   - If $ARGUMENTS includes `scope: project`, use `project` scope when calling scripts.

3. **Build the on-disk context pack**
   - From repo root, run:
     - `.specify/scripts/bash/build-context-pack.sh --json [--scope=project|feature]`
   - Parse the JSON output to obtain:
     - `CONTEXT_ROOT` (relative to repo root, e.g. `.speckit/context`).
     - `CONTEXT_JSON` (e.g. `.speckit/context/context.json`).
     - `FILES[]` metadata for copied artifacts.

4. **(Optional) Normalisation with speckit.bundle**
   - Use the `.claude/commands/speckit.bundle.md` definition to refine and normalise the contents of `CONTEXT_JSON` if needed:
     - Ensure that the JSON matches the Context Pack data model from `specs/006-ai-extensions/data-model.md`.
     - Add or refine `techStack[]` and `constraints[]` based on `plan.md`, constitution, and research docs.

5. **Report**
   - Present a short Markdown summary including:
     - Scope used (`project` or `feature`).
     - `CONTEXT_JSON` path.
     - A small table of files with their roles.

## Notes

- This workflow is intended to be safe and idempotent; repeated runs should update `context.json` and file copies without duplication.
- Only design-time markdown artifacts are included by default; code is excluded unless a future iteration explicitly adds configuration for it.

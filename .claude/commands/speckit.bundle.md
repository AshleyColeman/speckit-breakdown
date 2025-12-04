---
description: Build a context pack for AI agents and automation from existing SpecKit artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

User input may optionally include:
- `scope: project` or `scope: feature:<id>`
- Notes about which artifacts to prioritize (e.g., "focus on tasks and data model").

## Outline

1. **Determine scope and validate prerequisites**
   - From repo root, run:
     - `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks --require-advanced`
   - Parse JSON to get absolute paths for:
     - `REPO_ROOT`, `FEATURE_DIR`, `FEATURE_SPEC`, `IMPL_PLAN`, `TASKS`
   - Decide scope:
     - Default: `feature` (current feature only).
     - If $ARGUMENTS includes `scope: project`, use `project` scope.

2. **Prepare context pack on disk**
   - From repo root, run:
     - `.specify/scripts/bash/build-context-pack.sh --json [--scope=project|feature]`
   - Parse JSON output to get:
     - `SCOPE`
     - `CONTEXT_ROOT` (e.g., `.speckit/context`)
     - `CONTEXT_JSON` (e.g., `.speckit/context/context.json`)
     - `FILES` array with discovered file paths and roles.
   - Treat this JSON as the canonical on-disk representation of the context pack.

3. **Load input artifacts**
   - For the resolved feature (and project, if applicable), read:
     - `spec.md`, `plan.md`, `tasks.md`, `architecture.md` (if present)
     - `research.md`, `data-model.md`, `quickstart.md` (if present)
     - Any other design-time markdown files registered in `FILES`.
   - Do **not** include source code or non-design artifacts unless explicitly configured.

4. **Normalise context metadata**
   - Using the loaded artifacts and data-model definitions from `specs/006-ai-extensions/data-model.md`, normalise `context.json` so that:
     - It conforms to the **Context Pack** schema:
       - `id`, `projectName`, `featureId` (or `null` for project scope), `version`, `generatedAt`, `files[]`, `techStack[]`, `constraints[]`.
     - Each entry in `files[]` has:
       - `path`: repo-relative path
       - `role`: `spec` | `plan` | `tasks` | `architecture` | `tech-stack` | `other`
       - `title`: human-readable title
       - `contentStrategy`: `full` | `truncated` | `summary`
     - `techStack[]` and `constraints[]` reflect information from `plan.md`, constitution, and other design docs.
   - You may start from the JSON produced by `build-context-pack.sh` and refine/extend it.

5. **Write or update `context.json`**
   - Use `write_to_file` to create or overwrite the file at `CONTEXT_JSON`.
   - Ensure the JSON is valid, pretty-printed, and idempotent (re-running should update rather than duplicate entries).

6. **Report back**
   - Summarise the context pack in Markdown:
     - `SCOPE` used
     - `CONTEXT_JSON` path
     - Number of files and their roles
     - High-level notes on included tech stack and constraints.

## Context Pack Structure (Guideline)

When updating `context.json`, prefer a structure like:

```json
{
  "id": "feature-006-ai-extensions",
  "projectName": "speckit-breakdown",
  "featureId": "006-ai-extensions",
  "version": "1.0.0",
  "generatedAt": "2025-01-01T12:00:00Z",
  "files": [
    {
      "path": "specs/006-ai-extensions/spec.md",
      "role": "spec",
      "title": "Feature Specification",
      "contentStrategy": "full"
    },
    {
      "path": "specs/006-ai-extensions/plan.md",
      "role": "plan",
      "title": "Implementation Plan",
      "contentStrategy": "full"
    }
  ],
  "techStack": [
    { "name": "Bash", "version": "5.x", "category": "scripting" }
  ],
  "constraints": [
    "No destructive git operations",
    "Design-time markdown only by default"
  ]
}
```

Adjust IDs, paths, and fields according to the actual feature and project. Always ground values in the existing design documents and research decisions.

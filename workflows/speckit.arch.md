---
description: Generate or update an architecture.md snapshot for a SpecKit project or feature using existing design artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

User input may optionally specify:
- `scope: project` or `scope: feature:<id>`
- Any notes about which aspects of the architecture to focus on.

## Outline

1. **Setup & prerequisite check**
   - From the repository root, run:
     - `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks --require-advanced`
   - Parse the JSON output to get:
     - `FEATURE_DIR`, `FEATURE_SPEC`, `IMPL_PLAN`, `TASKS`
   - All paths MUST be treated as absolute.

2. **Resolve architecture scope and output path**
   - Decide scope:
     - Default: `feature` (current feature only).
     - If user input contains `scope: project`, use `project` scope.
   - Run, from repo root:
     - `.specify/scripts/bash/build-architecture.sh --json [--scope=project|feature]`
   - Parse the JSON result to get:
     - `SCOPE`, `ARCH_PATH`, and confirm `FEATURE_DIR`, `FEATURE_SPEC`, `IMPL_PLAN`, `TASKS`.

3. **Load context for architecture synthesis**
   - Read, at minimum:
     - `FEATURE_SPEC` (spec.md)
     - `IMPL_PLAN` (plan.md)
     - `TASKS` (tasks.md)
   - If present, also read from `FEATURE_DIR`:
     - `research.md`
     - `data-model.md`
   - If a previous architecture document exists at `ARCH_PATH`, read it as an additional input but be ready to replace it.

4. **Generate architecture snapshot using `speckit.arch` command**
   - Use the `.claude/commands/speckit.arch.md` definition as the primary guide.
   - Synthesize a clear, technology-agnostic architecture snapshot that:
     - Reflects the current spec, plan, tasks, and (optionally) research/data model.
     - Is understandable by both technical and non-technical stakeholders.
     - Matches the structure suggested in the command file (Context, Overview, Components, Data Flows, Dependencies, Decisions, Risks).

5. **Write or update the architecture document**
   - Use `write_to_file` to **create or overwrite** the file at `ARCH_PATH` with the generated architecture content.
   - Ensure the document is valid Markdown and can be committed as-is.
   - Do **not** modify any other files in this step.

6. **Report**
   - Summarize the result back to the user:
     - `SCOPE` used
     - `ARCH_PATH` of the generated document
     - 3–5 bullet summary of the architecture for quick review.

## Notes

- Always prefer **existing SpecKit artifacts** over invented structure.
- If there are ambiguities or missing pieces, call them out explicitly in the **Risks & Open Questions** section instead of guessing.
- Keep the document stable and idempotent: re-running `/speckit.arch` with the same inputs should produce an updated but non-duplicated architecture document.

---
description: Generate an architecture snapshot document for a project or feature based on existing SpecKit artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

User input may optionally include:
- A scope hint: `project` or `feature:<id>`
- Any notes about which aspects of architecture to emphasize

## Outline

1. **Determine scope and paths**
   - From repo root, run:
     - `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` to get `FEATURE_DIR`, `FEATURE_SPEC`, `IMPL_PLAN`, and `TASKS`.
     - `.specify/scripts/bash/build-architecture.sh --json` (with optional `--scope` argument derived from $ARGUMENTS) to get:
       - `SCOPE` (`project` or `feature`)
       - `ARCH_PATH` (absolute path where the architecture document should live)
   - Treat these JSON outputs as canonical for where to read and write.

2. **Load design context**
   - Read, from the resolved `FEATURE_DIR`:
     - `spec.md` (feature specification, user stories, acceptance scenarios, edge cases)
     - `plan.md` (technical context, project structure, constraints)
     - `tasks.md` (phase structure and implementation strategy)
   - If present, also read:
     - `architecture.md` at `ARCH_PATH` (existing architecture, to be updated)
     - `research.md` (key decisions and trade-offs)
     - `data-model.md` (entities and relationships)
   - Use these as the **single source of truth**; do not invent technologies or components not implied by these docs.

3. **Synthesize architecture snapshot**
   - Produce a clear, non-implementation-specific architecture document suitable for both technical and non-technical stakeholders.
   - Organize the document with sections like:
     - Title and scope
     - Context and goals (from spec + plan)
     - High-level system overview
     - Components and responsibilities
     - Data model and flows
     - External dependencies and integrations
     - Constraints and key decisions
     - Open questions / risks (if any remain)
   - Keep terminology aligned with the existing SpecKit documents.

4. **Write/update the architecture document**
   - Use `write_to_file` to **create or overwrite** the file at `ARCH_PATH`.
   - Ensure the file is valid Markdown and can be committed directly.
   - Do **not** modify any other files.

5. **Report back**
   - Summarize:
     - Scope (`project` or `feature`)
     - Output path of the architecture document
     - A 3–5 bullet summary of the architecture for quick review.

## Architecture Document Structure (Guideline)

When generating the architecture document, prefer a structure like:

```markdown
# Architecture: [Project or Feature Name]

**Scope**: [Project|Feature <id>]
**Source Artifacts**: spec.md, plan.md, tasks.md[, research.md, data-model.md]
**Last Updated**: [YYYY-MM-DD]

## 1. Context & Goals
- [High-level description of what this project/feature does]
- [Primary user groups]
- [Key outcomes and success criteria]

## 2. High-Level Overview
- [Short narrative description of the system/feature]
- [List of main components/modules]

## 3. Components & Responsibilities
- **Component A** – [role, key responsibilities]
- **Component B** – [role, key responsibilities]
- ...

## 4. Data Model & Flows
- [Summary of important entities from data-model.md]
- [Key relationships]
- [High-level data flows between components]

## 5. External Dependencies
- [APIs, services, queues, storage, etc.]

## 6. Constraints & Key Decisions
- [Important architectural constraints]
- [Decisions from research.md and plan.md]

## 7. Risks & Open Questions
- [Any remaining risks or decisions explicitly called out in the design docs]
```

Follow this structure as closely as possible while respecting the content of the existing SpecKit artifacts.

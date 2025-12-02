# Implementation Plan: Additional SpecKit Commands

**Branch**: `002-additional-commands` | **Date**: 2025-12-02 | **Spec**: [specs/002-additional-commands/spec.md]
**Input**: Feature specification for additional slash commands.

## Summary

Implement three additional slash commands (`/speckit.planreview`, `/speckit.techstack`, `/speckit.taskfile`) to further enhance the SpecKit workflow. These complement the core commands by adding plan validation, tech stack consistency checks, and agentic task isolation.

## Technical Context

**Language/Version**: Markdown (Prompt Engineering) + Bash (Scripting)
**Primary Dependencies**: SpecKit Core (`.specify/` scripts)
**Storage**: File-based (`tasks.md`, `plan.md`, `tasks/` directory)
**Project Type**: Tooling / Workflow Extension

## Constitution Check

*GATE: Passed.* These tools directly support the "Spec-Driven" and "Library-First" (via tech stack consistency) principles.

## Project Structure

### Documentation (this feature)

```text
specs/002-additional-commands/
├── plan.md              # This file
├── spec.md              # Feature specification
└── tasks.md             # To be generated
```

### Source Code (repository root)

```text
.claude/commands/
├── speckit.planreview.md       # [NEW] Plan review agent prompt
├── speckit.techstack.md        # [NEW] Tech stack analysis prompt
└── speckit.taskfile.md         # [NEW] Task file generator prompt

.specify/scripts/bash/
└── create-task-doc.sh          # [NEW] Helper script for task file creation
```

## Implementation Strategy

### Phase 1: Review & Analysis Commands

1.  **Plan Review Command**: Create `.claude/commands/speckit.planreview.md`.
    *   **Logic**: Load `plan.md`, `spec.md`, and `constitution.md`. Prompt agent to verify that the plan satisfies all spec requirements and adheres to constitution principles.
2.  **Tech Stack Command**: Create `.claude/commands/speckit.techstack.md`.
    *   **Logic**: Load `plan.md` and project context. Suggest specific libraries/versions for "NEEDS CLARIFICATION" items.

### Phase 2: Task Isolation (Agentic Workflow)

1.  **Task File Command**: Create `.claude/commands/speckit.taskfile.md`.
    *   **Logic**:
        *   Input: Task ID.
        *   Action: Extract context and generate a file.
        *   Tool Use: Use `run_command` to invoke `create-task-doc.sh`.
2.  **Creation Script**: Create `.specify/scripts/bash/create-task-doc.sh`.
    *   **Function**: Accepts Task ID, Title, and Context.
    *   **Logic**:
        1.  Create `tasks/` directory if missing.
        2.  Sanitize title for filename (e.g., `T001-implement-login.md`).
        3.  Write content using a standard template (Header, Context, Acceptance Criteria).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New Bash Script | Consistent file generation | Ensuring consistent filenames and template structure is better handled by a script than an LLM directly writing files. |

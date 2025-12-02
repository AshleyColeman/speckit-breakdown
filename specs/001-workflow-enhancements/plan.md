# Implementation Plan: SpecKit Workflow Enhancements

**Branch**: `001-workflow-enhancements` | **Date**: 2025-12-02 | **Spec**: [specs/001-workflow-enhancements/spec.md]
**Input**: Feature specification for new slash commands.

## Summary

Implement three new slash commands (`/speckit.specreview`, `/speckit.taskreview`, `/speckit.parallelize`) to enhance the quality assurance and velocity of the SpecKit workflow. These will be implemented as Markdown prompt files in `.claude/commands/` and potentially supported by bash scripts for logic where needed.

## Technical Context

**Language/Version**: Markdown (Prompt Engineering) + Bash (Scripting)
**Primary Dependencies**: SpecKit Core (`.specify/` scripts)
**Storage**: File-based (`tasks.md`, `spec.md`)
**Project Type**: Tooling / Workflow Extension

## Constitution Check

*GATE: Passed.* The proposed enhancements align with the "Spec-Driven" and "Test-First" principles by adding explicit validation steps (reviews) and automation (parallelization).

## Project Structure

### Documentation (this feature)

```text
specs/001-workflow-enhancements/
├── plan.md              # This file
├── spec.md              # Feature specification
└── tasks.md             # To be generated
```

### Source Code (repository root)

```text
.claude/commands/
├── speckit.specreview.md       # [NEW] Spec review agent prompt
├── speckit.taskreview.md       # [NEW] Task review agent prompt
└── speckit.parallelize.md      # [NEW] Parallel task expansion agent prompt

.specify/scripts/bash/
└── expand-tasks.sh             # [NEW] Helper script for task insertion (if needed)
```

## Implementation Strategy

### Phase 0: Foundation Fixes

1.  **Fix Feature Creation Script**: Patch `.specify/scripts/bash/create-new-feature.sh` to silence `git fetch` output. This prevents "value too great for base" errors during feature generation.

### Phase 1: Review Commands (Quality)

1.  **Spec Review Command**: Create `.claude/commands/speckit.specreview.md`.
    *   **Logic**: Load `spec.md` and `constitution.md`. Prompt the agent to act as a "Senior Architect" and critique the spec against the constitution and general quality heuristics (clarity, testability).
2.  **Task Review Command**: Create `.claude/commands/speckit.taskreview.md`.
    *   **Logic**: Load `tasks.md` and `plan.md`. Prompt the agent to act as a "Project Manager" and validate task granularity, dependencies, and formatting.

### Phase 2: Parallelization Command (Velocity)

1.  **Parallelize Command**: Create `.claude/commands/speckit.parallelize.md`.
    *   **Logic**:
        *   Input: A task description or ID.
        *   Context: `plan.md` (to understand architecture) and `tasks.md` (to know where to insert).
        *   Action: Generate a list of sub-tasks in a structured JSON block.
        *   Tool Use: The agent will use `run_command` to invoke `expand-tasks.sh` with the JSON payload.
2.  **Expansion Script**: Create `.specify/scripts/bash/expand-tasks.sh`.
    *   **Function**: Accepts a Task ID (parent) and a list of new task descriptions.
    *   **Logic**:
        1.  Scan `tasks.md` to find the highest existing Task ID (e.g., T050).
        2.  Assign new IDs starting from Max+1 (T051, T052...) to the new tasks.
        3.  Find the line number of the parent task.
        4.  Insert the new tasks immediately after the parent task, preserving indentation.
        5.  Mark the parent task as `[x]` (completed/expanded) or convert it to a section header to indicate it has been broken down.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New Bash Script | Reliable file manipulation for task insertion | LLM direct file editing can be flaky with large lists; a script ensures integrity of the task list structure. |

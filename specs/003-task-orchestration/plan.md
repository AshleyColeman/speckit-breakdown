# Implementation Plan: Task Orchestration

**Branch**: `003-task-orchestration` | **Date**: 2025-12-02 | **Spec**: [specs/003-task-orchestration/spec.md]
**Input**: Feature specification for `/speckit.orchestrate`.

## Summary

Implement `/speckit.orchestrate`, a command that "compiles" the `tasks.md` list into a set of executable, ordered task files. This moves SpecKit from a planning tool to an execution engine.

## Technical Context

**Language/Version**: Markdown (Prompt) + Bash (Scripting)
**Primary Dependencies**: SpecKit Core, Feature 002 (`create-task-doc.sh` logic will be expanded/referenced).
**Storage**: `tasks/` directory (will be populated with many files).

## Constitution Check

*GATE: Passed.* Aligns with "Spec-Driven" and enables "Agentic" workflows by making tasks machine-readable and independently executable.

## Project Structure

### Documentation

```text
specs/003-task-orchestration/
├── plan.md
├── spec.md
└── tasks.md
```

### Source Code

```text
.claude/commands/
└── speckit.orchestrate.md      # [NEW] Orchestration agent prompt

.specify/scripts/bash/
└── orchestrate-tasks.sh        # [NEW] Batch generation script
```

## Implementation Strategy

### Phase 1: The Orchestrator Script

1.  **Script**: Create `.specify/scripts/bash/orchestrate-tasks.sh`.
    *   **Input**: A JSON blob representing the parsed task list with order metadata.
    *   **Logic**:
        *   Iterate through the JSON list.
        *   For each task, call the existing logic (or script) to generate the file.
        *   Inject the `order` and `parallel` metadata into the file header.

### Phase 2: The Orchestrator Command

1.  **Prompt**: Create `.claude/commands/speckit.orchestrate.md`.
    *   **Context**: `tasks.md`, `spec.md`, `plan.md`.
    *   **Logic**:
        1.  Parse `tasks.md` line by line.
        2.  Identify Phases (headers) and Parallel groups (`[P]`).
        3.  Assign an incrementing `SequenceID` to each group of tasks.
### Phase 3: Update Implement Command

1.  **Update Prompt**: Modify `.claude/commands/speckit.implement.md`.
    *   **Logic**:
        *   Check if argument is a file path (ends in `.md`).
        *   If yes, `read_file <ARG>`.
        *   If no (or empty), fall back to legacy behavior (read `tasks.md` and ask user).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Large JSON Payload | Batch processing | Calling `create-task-doc.sh` 50 times individually via LLM tools is slow and error-prone. Passing a batch JSON to a script is atomic and fast. |

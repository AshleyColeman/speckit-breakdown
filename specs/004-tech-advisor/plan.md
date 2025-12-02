# Implementation Plan: Tech Stack Advisor

**Branch**: `004-tech-advisor` | **Date**: 2025-12-02 | **Spec**: [specs/004-tech-advisor/spec.md]
**Input**: Feature specification for `/speckit.techadvisor`.

## Summary

Implement `/speckit.techadvisor`, an interactive slash command that helps the user define the technology stack for a feature. Unlike the passive `/speckit.techstack` (which checks consistency), this tool actively helps *choose* the stack through analysis and dialogue.

## Technical Context

**Language/Version**: Markdown (Prompt Engineering)
**Primary Dependencies**: SpecKit Core
**Storage**: None (Interactive output).

## Constitution Check

*GATE: Passed.* Supports "Library-First" principle by encouraging thoughtful selection of technologies before coding.

## Project Structure

### Documentation

```text
specs/004-tech-advisor/
├── plan.md
├── spec.md
└── tasks.md
```

### Source Code

```text
.claude/commands/
└── speckit.techadvisor.md      # [NEW] Interactive advisor prompt
```

## Implementation Strategy

### Phase 1: The Advisor Prompt

1.  **Prompt**: Create `.claude/commands/speckit.techadvisor.md`.
    *   **Context**: `spec.md`, `constitution.md`.
    *   **Role**: "Senior Tech Lead" / "Solutions Architect".
    *   **Logic**:
        1.  Analyze `spec.md` for technical needs (DB, API, UI).
        2.  Check `constitution.md` for constraints (e.g., "Must use Postgres").
        3.  Identify open decisions (e.g., "Which state management lib?").
        4.  **Loop**: Ask User questions to resolve open decisions.
        5.  **Final**: Output a recommended stack block.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Interactive Loop | User Preference | We cannot guess user preferences (e.g., "Do you know React Query?"). Interaction is required for a good recommendation. |

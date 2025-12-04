# Implementation Plan: Advanced SDD Workflows

**Branch**: `005-advanced-sdd` | **Date**: 2025-12-03 | **Spec**: [specs/005-advanced-sdd/spec.md]

## Summary

Implement the "Holy Grail" of SDD: Test-First Generation, Self-Healing Implementation loops, and Reverse Synchronization.

## Technical Context

**Language**: Markdown (Prompts)
**Dependencies**: Existing SpecKit commands.

## Project Structure

### Source Code

```text
.claude/commands/
├── speckit.testgen.md          # [NEW] Generates tests
├── speckit.sync.md             # [NEW] Syncs code -> spec
└── speckit.implement.md        # [UPDATE] Adds self-healing loop instructions
```

## Implementation Strategy

### Phase 1: Test Generation (`/speckit.testgen`)

1.  **Prompt**: Create `.claude/commands/speckit.testgen.md`.
    *   **Context**: Task file, `plan.md` (for test runner/lib info).
    *   **Goal**: Output code blocks for test files.
    *   **Instruction**: "Write tests that assert the requirements in the task. Do not write implementation."

### Phase 2: Self-Healing (`/speckit.implement`)

1.  **Update Prompt**: Modify `.claude/commands/speckit.implement.md`.
    *   **Add Logic**:
        *   AFTER implementation: "Run tests using `npm test` (or equivalent)."
        *   IF FAIL: "Read error output. Fix code. Retry."
        *   LOOP: "Repeat up to 3 times."

### Phase 3: Synchronization (`/speckit.sync`)

1.  **Prompt**: Create `.claude/commands/speckit.sync.md`.
    *   **Context**: `spec.md`, User-selected code files.
    *   **Goal**: Compare Code vs Spec.
    *   **Output**: "Proposed Changes to Spec.md".

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Agent Loop | Self-Healing | Manual "Implement -> Fail -> User Fix" is too slow. Agent must own the fix loop. |

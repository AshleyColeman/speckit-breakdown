---
description: "Task list for advanced SDD workflows (005)"
---

# Tasks: Advanced SDD

**Input**: Design documents from `specs/005-advanced-sdd/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Test Generation (TDD)

**Purpose**: Generate tests before implementation.

- [x] T001 [US1] Create `.claude/commands/speckit.testgen.md`.
    - **Context**: Task file, `plan.md`.
    - **Goal**: Generate failing test files based on task requirements.

## Phase 2: Self-Healing Implementation

**Purpose**: Automate the fix loop.

- [x] T002 [US2] Update `.claude/commands/speckit.implement.md`.
    - **Change**: Add "Test-Fix-Retry" loop instructions.
    - **Logic**: Run tests -> If fail, read error -> Fix code -> Retry (Max 3).

## Phase 3: Synchronization

**Purpose**: Keep docs in sync with code.

- [x] T003 [US3] Create `.claude/commands/speckit.sync.md`.
    - **Context**: `spec.md`, Codebase.
    - **Goal**: Compare code to spec and suggest spec updates.

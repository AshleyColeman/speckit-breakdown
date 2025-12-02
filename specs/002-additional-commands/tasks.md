---
description: "Task list for additional commands (002)"
---

# Tasks: Additional SpecKit Commands

**Input**: Design documents from `specs/002-additional-commands/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Review & Analysis Commands

**Purpose**: Implement Plan Review and Tech Stack Analysis tools.

- [x] T001 [P] [US1] Create `.claude/commands/speckit.planreview.md` prompt.
    - **Context**: Load `plan.md`, `spec.md`, and `constitution.md`.
    - **Goal**: Verify plan satisfies spec requirements and constitution.
- [x] T002 [P] [US2] Create `.claude/commands/speckit.techstack.md` prompt.
    - **Context**: Load `plan.md` and project context.
    - **Goal**: Suggest libraries/versions for undefined items based on existing stack.

## Phase 2: Task Isolation (Agentic Workflow)

**Purpose**: Implement the Task File generator for focused agent execution.

- [x] T003 [US3] Create `.specify/scripts/bash/create-task-doc.sh`.
    - **Logic**: Accept Task ID, Title, Context. Create `tasks/` dir. Write formatted markdown file `tasks/Txxx-title.md`.
- [x] T004 [US3] Create `.claude/commands/speckit.taskfile.md` prompt.
    - **Context**: Load `tasks.md`, `spec.md`, `plan.md`.
    - **Action**: Extract context for specific task and call `create-task-doc.sh`.

## Dependencies & Execution Order

- **Phase 1** and **Phase 2** can run in parallel.

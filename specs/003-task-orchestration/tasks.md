---
description: "Task list for task orchestration (003)"
---

# Tasks: Task Orchestration

**Input**: Design documents from `specs/003-task-orchestration/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: The Orchestrator Script

**Purpose**: Batch generation of task files.

- [x] T001 [US1] Create `.specify/scripts/bash/orchestrate-tasks.sh`.
    - **Logic**: Accept JSON list of tasks with metadata (ID, Order, Parallel). Call `create-task-doc.sh` (or internal logic) to generate each file. Ensure YAML frontmatter is correct.

## Phase 2: The Orchestrator Command

**Purpose**: The agent prompt that calculates the schedule.

- [x] T002 [US1] Create `.claude/commands/speckit.orchestrate.md`.
    - **Context**: Load `tasks.md`, `spec.md`, `plan.md`.
    - **Goal**: Parse task list, calculate execution order/parallel groups, generate JSON, call script.

## Phase 3: Update Implement Command

**Purpose**: Allow agents to consume the orchestrated files.

- [x] T003 [US2] Update `.claude/commands/speckit.implement.md`.
    - **Change**: Add logic to check if input is a file path. If so, read ONLY that file. If not, fallback to default.

## Dependencies & Execution Order

- T001 and T002 are coupled. T003 can be done independently but is needed to *use* the output of T001/T002.

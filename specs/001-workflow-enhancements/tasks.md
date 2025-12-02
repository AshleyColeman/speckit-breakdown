---
description: "Task list for workflow enhancements (001)"
---

# Tasks: SpecKit Workflow Enhancements

**Input**: Design documents from `specs/001-workflow-enhancements/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 0: Foundation Fixes (Blocking)

**Purpose**: Fix known issues that block reliable automation.

- [x] T001 [FR-007] Patch `.specify/scripts/bash/create-new-feature.sh` to silence `git fetch` output to prevent "value too great for base" errors.

## Phase 1: Review Commands (Quality)

**Purpose**: Implement the review agents for Spec and Task files.

- [x] T002 [P] [US1] Create `.claude/commands/speckit.specreview.md` prompt.
    - **Context**: Must load `spec.md` and `constitution.md`.
    - **Goal**: Critique spec against constitution and quality heuristics.
- [x] T003 [P] [US2] Create `.claude/commands/speckit.taskreview.md` prompt.
    - **Context**: Must load `tasks.md` and `plan.md`.
    - **Goal**: Validate task granularity, dependencies, and formatting.

## Phase 2: Parallelization Command (Velocity)

**Purpose**: Implement the parallel task expansion workflow.

- [x] T004 [US3] Create `.specify/scripts/bash/expand-tasks.sh`.
    - **Logic**: Accept Task ID and JSON list of new tasks. Find Max ID in `tasks.md`. Insert new tasks with IDs starting at Max+1. Mark parent as processed.
- [x] T005 [US3] Create `.claude/commands/speckit.parallelize.md` prompt.
    - **Context**: Load `tasks.md` and `plan.md`.
    - **Action**: Generate JSON payload for sub-tasks and call `expand-tasks.sh`.

## Dependencies & Execution Order

- **Phase 0** blocks everything (script reliability).
- **Phase 1** and **Phase 2** can run in parallel after Phase 0.

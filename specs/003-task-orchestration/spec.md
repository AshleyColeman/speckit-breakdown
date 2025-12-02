# Feature Specification: Task Orchestration & Materialization

**Feature Branch**: `003-task-orchestration`
**Created**: 2025-12-02
**Status**: Draft
**Input**: User request for a command to generate separate task files with execution order and parallelization metadata.

## User Scenarios & Testing

### User Story 1 - Task Orchestration Command (Priority: P1)

As a developer, I want to run `/speckit.orchestrate` to process my entire `tasks.md` list and generate individual markdown files for every task (e.g., `tasks/01-T001-setup.md`), where each file contains explicit metadata about its **Execution Order** and **Parallel Group**, so that I can execute them sequentially or in parallel with agents without manual coordination.

**Why this priority**: Enables fully automated or "swarm" execution where agents know exactly when to pick up a task.

**Independent Test**:
1. Create a `tasks.md` with:
    - Task A (Phase 1)
    - Task B (Phase 1)
    - Task C (Phase 2)
2. Run `/speckit.orchestrate`.
3. Verify 3 files are created.
4. Verify Task A and B have `Order: 1` (or similar) and Task C has `Order: 2`.

**Acceptance Scenarios**:
1. **Given** a `tasks.md` with 10 tasks, **When** I run the command, **Then** 10 files are generated in the `tasks/` directory.
2. **Given** tasks marked with `[P]` (parallel), **When** generated, **Then** they share the same `ExecutionOrder` or `SequenceNumber`.
3. **Given** a task that depends on previous phases, **When** generated, **Then** its `ExecutionOrder` is higher than its dependencies.

### User Story 2 - Task-Based Implementation (Priority: P1)

As a developer, I want `/speckit.implement` to accept a specific task file (e.g., `tasks/01-T001.md`) as input, so that the agent focuses ONLY on the context provided in that file (which was pre-calculated by the orchestrator), reducing noise and token usage.

**Why this priority**: Completes the "Orchestrated" workflow.

**Acceptance Scenarios**:
1. **Given** a task file `tasks/01-T001.md`, **When** I run `/speckit.implement tasks/01-T001.md`, **Then** the agent reads that file and executes the instructions within it.
2. **Then** the agent does NOT need to read the full `spec.md` or `plan.md` again, as the context is already in the task file.

## Requirements

### Functional Requirements

- **FR-001**: `/speckit.orchestrate` MUST read `tasks.md`, `spec.md`, and `plan.md`.
- **FR-002**: The command MUST parse the task list to determine the logical execution order (respecting Phases and `[P]` markers).
- **FR-003**: The command MUST generate a separate markdown file for **every** task in the list.
- **FR-004**: Each generated file MUST include YAML frontmatter with:
    - `id`: The Task ID (e.g., T001)
    - `order`: An integer representing the execution sequence.
    - `parallel`: Boolean, true if it can run in parallel with others in the same order.
- **FR-005**: The command MUST use a helper script (`orchestrate-tasks.sh`) to ensure consistent file generation.
- **FR-006**: `/speckit.implement` MUST be updated to accept a file path argument.
- **FR-007**: If a file path is provided, `/speckit.implement` MUST prioritize the context in that file over global context.

### Key Entities

- **OrchestratedTask**: A task file enriched with scheduling metadata.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of tasks in `tasks.md` result in a corresponding file in `tasks/`.
- **SC-002**: Generated files have strictly increasing `order` numbers across phases.

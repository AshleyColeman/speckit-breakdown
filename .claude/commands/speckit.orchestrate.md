---
description: Parse tasks.md and generate orchestrated task files
---

# SpecKit Orchestrator

You are a **Project Scheduler**. Your goal is to analyze the `tasks.md` file, determine the optimal execution order for all tasks, and generate individual task files for them.

## Context

1.  **Read the Tasks**: `read_file tasks.md`
2.  **Read the Plan**: `read_file plan.md`

## Instructions

1.  **Parse Task List**: Read `tasks.md` line by line.
2.  **Identify Phases**: Tasks under "Phase 1" come before "Phase 2".
3.  **Identify Parallelism**: Tasks marked with `[P]` in the same phase should have the same `order`.
4.  **Assign Order**:
    - Start with Order = 1.
    - Increment Order when moving between sequential tasks or phases.
    - Keep Order constant for a block of parallel tasks.
    - **Crucial**: Populate `"dependencies": ["PREVIOUS_TASK_ID"]`.
      - Tasks in Phase 2 MUST depend on tasks in Phase 1.
5.  **Assign Status**:
    - If Order = 1: Set `status: "ready"`
    - Else: Set `status: "pending"`
6.  **Construct JSON**: Create a JSON list of all tasks.
    ```json
    [
      {"id": "T001", "description": "Setup repo", "order": 1, "parallel": false, "phase": "Phase 0", "status": "ready", "dependencies": []},
      {"id": "T002", "description": "Create API", "order": 2, "parallel": true, "phase": "Phase 1", "status": "pending", "dependencies": ["T001"]},
      {"id": "T003", "description": "Create UI", "order": 2, "parallel": true, "phase": "Phase 1", "status": "pending", "dependencies": ["T001"]}
    ]
    ```

## Execution

You must use the `run_command` tool to execute the orchestration script.

### Command Format

```bash
./.specify/scripts/bash/orchestrate-tasks.sh '<JSON_LIST>'
```

### Example Interaction

**User**: "Orchestrate tasks"

**Agent**:
1.  Reads `tasks.md`.
2.  Calculates schedule: T001 (Ord 1), T002 (Ord 2), T003 (Ord 2).
3.  Runs command:
    ```bash
    ./.specify/scripts/bash/orchestrate-tasks.sh '[{"id":"T001", "order":1...}, ...]'
    ```

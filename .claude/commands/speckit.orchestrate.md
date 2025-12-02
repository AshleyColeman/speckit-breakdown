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
5.  **Construct JSON**: Create a JSON list of all tasks.
    ```json
    [
      {"id": "T001", "description": "Setup repo", "order": 1, "parallel": false, "phase": "Phase 0"},
      {"id": "T002", "description": "Create API", "order": 2, "parallel": true, "phase": "Phase 1"},
      {"id": "T003", "description": "Create UI", "order": 2, "parallel": true, "phase": "Phase 1"}
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

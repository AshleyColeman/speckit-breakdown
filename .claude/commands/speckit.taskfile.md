---
description: Generate a dedicated markdown file for a specific task with context
---

# SpecKit Task File Generator

You are a **Project Coordinator**. Your goal is to prepare a dedicated workspace file for a specific task, gathering all relevant context from the project documentation so an agent can work on it in isolation.

## Context

1.  **Read the Tasks**: `read_file tasks.md`
2.  **Read the Spec**: `read_file spec.md`
3.  **Read the Plan**: `read_file plan.md`

## Instructions

1.  **Identify the Task**: The user will provide a Task ID (e.g., `T042`). Find it in `tasks.md`.
2.  **Extract Context**:
    - **Title**: The task description.
    - **User Story**: Find the relevant User Story in `spec.md`.
    - **Requirements**: Find relevant Functional Requirements in `spec.md`.
    - **Technical Details**: Find relevant implementation details in `plan.md`.
3.  **Synthesize Context**: Combine these into a concise markdown summary.

## Execution

You must use the `run_command` tool to create the file using the helper script.

### Command Format

```bash
./.specify/scripts/bash/create-task-doc.sh <TASK_ID> "<TITLE>" "<CONTEXT_MARKDOWN>"
```

### Example Interaction

**User**: "Create file for T005"

**Agent**:
1.  Finds T005: "Create database models".
2.  Extracts context:
    - Story: "As a user I want to save data..."
    - Tech: "Use Prisma schema..."
3.  Runs command:
    ```bash
    ./.specify/scripts/bash/create-task-doc.sh T005 "Create database models" "## User Story\nAs a user...\n\n## Tech Notes\nUse Prisma..."
    ```

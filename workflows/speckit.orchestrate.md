---
description: "Task orchestration workflow for parallel execution"
---

# Workflow: speckit.orchestrate

## Overview
Processes the entire task list and generates individual markdown files with execution order and parallelization metadata for automated agent execution.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `tasks.md` exists in the current feature directory
   - Ensure `spec.md` and `plan.md` exist for context

2. **Load Context**
   - Read `tasks.md` from the detected feature directory
   - Read `spec.md` for user story context
   - Read `plan.md` for technical approach
   - Parse all tasks with their metadata and dependencies

3. **Calculate Execution Order**
   - Analyze task phases and dependencies
   - Determine execution sequence:
     - Phase 1 tasks get Order 1
     - Phase 2 tasks get Order 2, etc.
   - Identify parallel tasks:
     - Tasks marked `[P]` share the same execution order
     - Tasks in the same phase without dependencies can run in parallel
   - Validate dependency graph (no circular dependencies)

4. **Generate Task Files**
   - Create JSON payload with all tasks and metadata:
     ```json
     {
       "tasks": [
         {
           "id": "T001",
           "title": "Task title",
           "description": "Full description",
           "order": 1,
           "parallel": true,
           "phase": "Phase 1"
         }
       ]
     }
     ```
   - Call `.specify/scripts/bash/orchestrate-tasks.sh` with JSON payload
   - Script creates individual files in `tasks/` directory
   - Each file includes YAML frontmatter with execution metadata

5. **Output Results**
   - Display summary of generated files
   - Show execution order and parallel groups
   - Provide guidance on running tasks in parallel
   - Explain how to use with `/speckit.implement <task-file>`

## Error Handling
- If no tasks file found, guide user to run `/speckit.tasks` first
- If circular dependencies detected, report and suggest fixes
- If task directory creation fails, check permissions

## Success Criteria
- 100% of tasks in `tasks.md` have corresponding files in `tasks/`
- Generated files have correct execution order and parallel metadata
- Dependency graph is validated and acyclic
- User can execute tasks using the generated files

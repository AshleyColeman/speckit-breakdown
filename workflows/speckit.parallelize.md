---
description: "Parallel task expansion workflow"
---

# Workflow: speckit.parallelize

## Overview
Expands high-level tasks into multiple parallel sub-tasks to accelerate implementation with parallel agents.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `tasks.md` exists in the current feature directory
   - Ensure `plan.md` exists for technical context

2. **Load Context**
   - Read `tasks.md` from the detected feature directory
   - Read `plan.md` for technical approach and constraints
   - Identify the target task for parallelization (from user input or selection)

3. **Analyze Target Task**
   - Parse the task description to identify parallelizable components
   - Look for patterns like:
     - "Create models for X, Y, and Z"
     - "Implement services for A, B, C"
     - "Build components for user, admin, guest"
   - Determine logical grouping strategy

4. **Generate Parallel Tasks**
   - Create individual task descriptions for each component
   - Generate unique task IDs (find current max ID + 1)
   - Mark all generated tasks with `[P]` for parallel execution
   - Maintain same phase as parent task
   - **Crucial**: Copy exact `dependencies` list from parent task into the Frontmatter of all new tasks.
     - This ensures `speckit.db.prepare` calculates them as correct siblings in the Step Order.

5. **Update Task List**
   - Call `.specify/scripts/bash/expand-tasks.sh` with generated tasks
   - Insert new tasks after the parent task in `tasks.md`
   - Preserve existing task ordering and formatting
   - Update parent task if needed (e.g., mark as coordination task)

6. **Output Results**
   - Show the generated tasks with their IDs
   - Explain the parallelization strategy used
   - Provide guidance on next steps for parallel execution

## Error Handling
- If target task not found, prompt user to select from available tasks
- If task not parallelizable, explain why and suggest alternatives
- If task ID conflicts occur, regenerate with proper sequencing

## Success Criteria
- Generated tasks are properly formatted and uniquely identified
- Parallel tasks are marked with `[P]` and share execution order
- Parent task context is preserved or appropriately updated
- User understands how to execute tasks in parallel

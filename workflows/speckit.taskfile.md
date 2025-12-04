---
description: "Individual task file generation workflow"
---

# Workflow: speckit.taskfile

## Overview
Generates a dedicated markdown file for a specific task containing all necessary context for focused agent execution.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `tasks.md` exists in the current feature directory
   - Ensure `spec.md` and `plan.md` exist for context extraction

2. **Load Context**
   - Read `tasks.md` from the detected feature directory
   - Read `spec.md` for requirement context
   - Read `plan.md` for technical approach context
   - Parse the target task ID from user input

3. **Extract Task Context**
   - Locate the specified task in `tasks.md`
   - Extract relevant user stories from `spec.md`
   - Gather technical details from `plan.md`:
     - Technology stack relevant to the task
     - File structure and patterns
     - Dependencies and interfaces
   - Include implementation notes and constraints

4. **Generate Task File**
   - Call `.specify/scripts/bash/create-task-doc.sh` with:
     - Task ID and title
     - Extracted context and requirements
     - Technical specifications
     - Dependencies and prerequisites
   - Create file in `tasks/` subdirectory with format `Txxx-title.md`
   - Include YAML frontmatter with metadata:
     - Task ID and order
     - Parallel execution flag
     - Dependencies

5. **Output Results**
   - Display the path to the generated task file
   - Show a summary of included context
   - Provide guidance on using the file with `/speckit.implement`
   - Explain how this enables focused agent execution

## Error Handling
- If no tasks file found, guide user to run `/speckit.tasks` first
- If task ID not found, list available tasks for selection
- If context files missing, warn that task file may be incomplete

## Success Criteria
- Generated task file contains all necessary context for implementation
- File is properly formatted with valid YAML frontmatter
- Agent can implement the task using only this file (no additional context needed)
- User understands how to use the task file for focused execution

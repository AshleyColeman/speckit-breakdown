---
description: "Task review workflow for task validation"
---

# Workflow: speckit.taskreview

## Overview
Validates a task list for proper formatting, logical dependencies, and implementation readiness.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `tasks.md` exists in the current feature directory
   - Ensure `plan.md` exists for context validation

2. **Load Context**
   - Read `tasks.md` from the detected feature directory
   - Read `plan.md` to understand technical approach
   - Load task formatting standards and conventions

3. **Execute Task Review**
   - Validate task formatting:
     - Proper checkbox format `[ ]` or `[x]`
     - Valid task IDs (T001, T002, etc.)
     - Clear, actionable descriptions
   - Analyze dependency logic:
     - Check for circular dependencies
     - Verify phase sequencing is logical
     - Validate parallel task markings `[P]`
   - Assess implementation readiness:
     - Tasks are sufficiently granular
     - No ambiguous requirements
     - Dependencies are explicitly stated

4. **Output Results**
   - Display structured review with severity levels:
     - **Critical**: Format errors, circular dependencies
     - **Major**: Missing dependencies, overly broad tasks
     - **Minor**: Style inconsistencies, unclear descriptions
   - Provide specific fixes for each identified issue
   - Include examples of properly formatted tasks

## Error Handling
- If no tasks file found, guide user to run `/speckit.tasks` first
- If plan file missing, warn that validation may be incomplete
- If formatting errors detected, provide before/after examples

## Success Criteria
- All format errors are identified with clear examples
- Dependency issues are highlighted with explanations
- Tasks are assessed for implementation readiness
- User receives actionable guidance for fixes

---
description: Review the current task list for logic, dependencies, and completeness
---

# SpecKit Task Review

You are a **Technical Project Manager** and **Engineering Lead**. Your goal is to review the current task list (`tasks.md`) against the Implementation Plan (`plan.md`) to ensure it is actionable, logical, and complete.

## Context

1.  **Read the Plan**: `read_file plan.md`
2.  **Read the Tasks**: `read_file tasks.md`

## Analysis Instructions

Analyze the task list for the following:

### 1. Structure & Format
- Do all tasks follow the regex `^- \[ \] T[0-9]{3} .*$`?
- Are tasks grouped into logical Phases?
- Are parallelizable tasks marked with `[P]`?

### 2. Logic & Dependencies
- Is the **Dependency Graph** acyclic? (No circular dependencies)
- Do "Foundational" phases actually precede the work that depends on them?
- Are there any "Magic Steps" (tasks that assume work is done without a corresponding task)?

### 3. Granularity
- Are tasks too large? (e.g., "Implement entire backend") -> Suggest breaking down.
- Are tasks too small? (e.g., "Create file", "Add import") -> Suggest grouping.
- **Rule of Thumb**: A task should take 1-4 hours to complete.

### 4. Alignment
- Do the tasks cover ALL requirements from the `plan.md`?
- Are there extra tasks not justified by the plan?

## Output Format

```markdown
# Task Review Report

## 1. Structural Validation
- [Pass/Fail] Format Check
- [Pass/Fail] Phase Organization

## 2. Logic & Dependencies
- [ ] **Issue**: Description of dependency issue.

## 3. Granularity & Scope
- [ ] **Observation**: Tasks that are too big/small.

## 4. Missing or Extraneous Tasks
- [ ] **Missing**: Requirement X from plan has no corresponding task.

## 5. Recommendation
[Proceed to Implementation / Refine Tasks]
```

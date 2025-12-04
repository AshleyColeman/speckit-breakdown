---
description: "Tech stack analysis workflow"
---

# Workflow: speckit.techstack

## Overview
Analyzes technology choices in a plan and suggests specific libraries/versions based on the project's existing stack and patterns.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `plan.md` exists in the current feature directory
   - Load project context from agent files and existing implementations

2. **Load Context**
   - Read `plan.md` from the detected feature directory
   - Extract current technology choices and "NEEDS CLARIFICATION" items
   - Load project's active technologies from:
     - `.specify/memory/` files
     - Existing feature implementations
     - Agent context files

3. **Analyze Technology Gaps**
   - Identify undefined or ambiguous technology choices:
     - "NEEDS CLARIFICATION" markers
     - Generic descriptions ("database", "UI framework")
     - Missing version specifications
   - Cross-reference with project's existing stack:
     - What databases are already used?
     - What UI frameworks are established?
     - What testing libraries are standard?

4. **Generate Recommendations**
   - Suggest specific libraries/versions for each gap:
     - Prioritize technologies already used in the project
     - Consider compatibility with existing stack
     - Recommend stable, well-supported versions
     - Provide reasoning for each suggestion
   - Include:
     - Library name and version
     - Installation command (if applicable)
     - Brief justification for the choice
     - Links to documentation or examples

5. **Output Results**
   - Display technology recommendations in structured format
   - Show before/after comparisons for plan updates
   - Provide copy-paste ready snippets for `plan.md`
   - Include migration notes if changing from existing choices

## Error Handling
- If no plan file found, guide user to run `/speckit.plan` first
- If project context insufficient, recommend establishing tech standards
- If no gaps found, confirm current technology choices are solid

## Success Criteria
- All technology gaps are filled with specific, actionable recommendations
- Suggestions are consistent with project's existing stack
- User receives ready-to-use plan updates
- Rationale is provided for each technology choice

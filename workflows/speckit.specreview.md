---
description: "Spec review workflow for quality assurance"
---

# Workflow: speckit.specreview

## Overview
Reviews a specification document against the project constitution and quality heuristics, providing actionable feedback for improvement.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `spec.md` exists in the current feature directory
   - Ensure `.specify/memory/constitution.md` exists

2. **Load Context**
   - Read `spec.md` from the detected feature directory
   - Read `.specify/memory/constitution.md` for project standards
   - Load any relevant project context from agent files

3. **Execute Spec Review**
   - Analyze the specification for:
     - Constitution compliance
     - Requirement clarity and completeness
     - User story quality and testability
     - Acceptance criteria specificity
     - Technical feasibility
   - Generate structured review with severity levels:
     - **Critical**: Constitution violations, missing essential sections
     - **Major**: Ambiguous requirements, incomplete user stories
     - **Minor**: Style issues, formatting improvements

4. **Output Results**
   - Display the review report in the editor
   - Include specific, actionable recommendations
   - Reference constitution sections where applicable
   - Suggest next steps for addressing issues

## Error Handling
- If no spec file found, guide user to run `/speckit.specify` first
- If constitution missing, guide user to run `/speckit.constitution`
- If project structure invalid, provide clear guidance

## Success Criteria
- All critical issues are clearly flagged
- Recommendations are specific and actionable
- Review references relevant constitution sections
- User understands next steps to improve the spec

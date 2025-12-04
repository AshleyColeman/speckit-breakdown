---
description: "Plan review workflow for architectural validation"
---

# Workflow: speckit.planreview

## Overview
Validates an implementation plan against the specification and constitution, ensuring all requirements are addressed and architectural standards are met.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `plan.md` exists in the current feature directory
   - Ensure `spec.md` exists for requirement cross-check
   - Ensure `.specify/memory/constitution.md` exists for standards validation

2. **Load Context**
   - Read `plan.md` from the detected feature directory
   - Read `spec.md` to understand requirements
   - Read `.specify/memory/constitution.md` for architectural standards
   - Load project technical context and constraints

3. **Execute Plan Review**
   - Cross-check plan against spec requirements:
     - Every user story has corresponding implementation approach
     - All functional requirements are addressed
     - Non-functional requirements are considered
   - Validate against constitution:
     - Technology choices comply with approved stack
     - Architectural patterns follow project standards
     - Security and performance considerations included
   - Assess implementation feasibility:
     - Technical approach is sound and achievable
     - Dependencies and risks are identified
     - Resource estimates are reasonable

4. **Output Results**
   - Display structured gap analysis:
     - **Critical Gaps**: Missing requirements, constitution violations
     - **Major Issues**: Incomplete approaches, architectural concerns
     - **Minor Suggestions**: Optimization opportunities, documentation improvements
   - Provide specific recommendations for addressing gaps
   - Reference spec sections and constitution clauses

## Error Handling
- If no plan file found, guide user to run `/speckit.plan` first
- If spec file missing, warn that validation may be incomplete
- If constitution missing, guide user to run `/speckit.constitution`

## Success Criteria
- All spec requirements are accounted for in the plan
- Constitution compliance is verified and documented
- Technical feasibility is assessed with clear rationale
- User receives actionable guidance for plan improvements

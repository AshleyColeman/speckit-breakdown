---
description: "Interactive tech stack advisor workflow"
---

# Workflow: speckit.techadvisor

## Overview
Provides an interactive consultation session to help developers choose appropriate technology stacks for their features based on requirements and project standards.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `spec.md` exists in the current feature directory
   - Ensure `.specify/memory/constitution.md` exists for project standards

2. **Load Context**
   - Read `spec.md` from the detected feature directory
   - Read `.specify/memory/constitution.md` for technology constraints
   - Load project's existing technology stack and patterns
   - Analyze requirements to identify technical components needed

3. **Interactive Analysis**
   - Present initial assessment of technical requirements:
     - Database needs (SQL vs NoSQL, scale requirements)
     - Authentication and authorization requirements
     - UI/UX framework needs
     - API patterns (REST, GraphQL, real-time)
     - Testing and deployment requirements
   - Ask clarifying questions for ambiguous areas:
     - "Do you prefer SQL or NoSQL for data storage?"
     - "Should this use Tailwind CSS or traditional CSS modules?"
     - "Do you need real-time capabilities (WebSockets) or is polling sufficient?"
     - "What's your preference for state management?"

4. **Generate Recommendations**
   - Based on user answers, suggest specific technology choices:
     - Database: PostgreSQL, MongoDB, etc. with reasoning
     - Framework: Next.js, Express, etc. with version
     - Authentication: NextAuth, Auth0, etc.
     - Testing: Jest, Cypress, etc.
     - Deployment: Vercel, Docker, etc.
   - Ensure recommendations comply with project constitution
   - Provide copy-paste ready "Technology Stack" section for `plan.md`

5. **Output Results**
   - Display recommended stack with clear reasoning
   - Provide installation commands and setup notes
   - Generate markdown block ready for insertion into `plan.md`
   - Include links to documentation and examples

## Error Handling
- If no spec file found, guide user to run `/speckit.specify` first
- If constitution missing, warn that recommendations may not comply with project standards
- If requirements are too vague, ask for more specific details

## Success Criteria
- User receives specific, actionable technology recommendations
- Recommendations are consistent with project standards and constitution
- Output is ready to paste into `plan.md`
- User understands the rationale behind each technology choice

---
description: "Test generation workflow for TDD approach"
---

# Workflow: speckit.testgen

## Overview
Generates a comprehensive test suite for a task before any implementation code is written, following Test-Driven Development principles.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure target task file exists (either in `tasks.md` or as individual task file)
   - Ensure `plan.md` exists for testing stack information
   - Validate that testing framework is configured in the project

2. **Load Context**
   - Read the task context (from task file or `tasks.md`)
   - Read `plan.md` to understand testing stack and patterns
   - Extract requirements and acceptance criteria for the task
   - Identify components, functions, or features that need testing

3. **Analyze Testing Requirements**
   - Determine test types needed based on task:
     - Unit tests for individual functions/components
     - Integration tests for API endpoints
     - Component tests for UI elements
     - E2E tests for user workflows
   - Identify test scenarios from acceptance criteria:
     - Happy path scenarios
     - Error handling and edge cases
     - Validation and security tests
     - Performance and accessibility tests

4. **Generate Test Files**
   - Create test file(s) following project conventions:
     - `src/components/ComponentName.test.tsx` for React components
     - `src/api/endpoint.test.ts` for API routes
     - `src/utils/function.test.ts` for utility functions
   - Write failing tests that cover all requirements:
     - Test structure follows Arrange-Act-Assert pattern
     - Tests are descriptive and self-documenting
     - Mock external dependencies appropriately
     - Include setup and teardown as needed
   - Ensure tests compile but fail (red state in TDD)

5. **Output Results**
   - Display paths to generated test files
   - Show summary of test coverage and scenarios
   - Provide guidance on running tests and seeing failures
   - Explain next steps for implementation (make tests green)

## Error Handling
- If no task specified, prompt user to provide task ID or file path
   - If testing framework not configured, guide user to set it up first
   - If plan doesn't specify testing stack, recommend project standards

## Success Criteria
- Generated test files are comprehensive and cover all requirements
- Tests are properly structured and follow project conventions
- Tests fail initially but compile without errors
- User has clear path forward for implementation

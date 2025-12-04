---
description: "Spec synchronization workflow for keeping docs in sync with code"
---

# Workflow: speckit.sync

## Overview
Compares the actual codebase against the specification and identifies discrepancies, suggesting updates to keep documentation current.

## Steps

1. **Prerequisites Check**
   - Run `.specify/scripts/bash/check-prerequisites.sh` to validate project structure
   - Ensure `spec.md` exists in the current feature directory
   - Scan codebase for implemented files and features

2. **Load Context**
   - Read `spec.md` from the detected feature directory
   - Analyze project structure and implemented files:
     - Source code files in `src/` directories
     - Configuration files
     - Database schemas/migrations
     - API routes and endpoints
     - Component files
   - Parse current specification entities and requirements

3. **Perform Code-Spec Comparison**
   - Identify discrepancies between code and specification:
     - **Missing in Spec**: Features implemented but not documented
       - New fields in data models
       - Additional API endpoints
       - Extra components or utilities
     - **Missing in Code**: Spec features not yet implemented
       - Specified entities without corresponding code
       - Requirements not reflected in implementation
     - **Inconsistent**: Differences between spec and code
       - Different field names or types
       - Mismatched API signatures
       - Outdated documentation

4. **Generate Sync Report**
   - Create structured discrepancy report:
     - List each missing specification item with suggested additions
     - List each missing implementation item with priority
     - Highlight inconsistencies with specific recommendations
     - Include file paths and line numbers where applicable
   - Provide copy-paste ready updates for `spec.md`
   - Suggest implementation tasks for missing code

5. **Output Results**
   - Display comprehensive sync report
   - Show before/after comparisons for specification updates
   - Prioritize recommendations by impact
   - Provide guidance on applying the updates

## Error Handling
- If no spec file found, guide user to run `/speckit.specify` first
- If codebase scan fails, check permissions and project structure
- If too many discrepancies found, suggest focusing on high-priority items

## Success Criteria
- All discrepancies between code and specification are identified
- Recommendations are specific and actionable
- User receives ready-to-apply specification updates
- Implementation gaps are clearly documented with priorities

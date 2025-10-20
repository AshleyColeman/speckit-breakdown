---
description: Break down a complete project into individual feature specifications that can be processed with speckit.specify
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command transforms a **complete project plan** (with all features) into **individual feature specifications** that can each be processed through the SpecKit workflow (specify → clarify → plan → tasks → implement).

**CRITICAL**: This workflow MUST create actual files using `write_to_file` tool. Do not just present the content - actually create:
- `docs/project-breakdown.md` (master breakdown)
- `docs/features/feature-[ID]-description.md` (one file per feature)
- `docs/features/quick-start.sh` (command reference)

### Step 1: Locate or Create Project Plan

1. **Check for existing project plan**:
   - Look for files like: `project-plan.md`, `PROJECT.md`, `README.md`, or files mentioned in $ARGUMENTS
   - If user provided a file path in $ARGUMENTS, use that
   - If no file specified, ask user which file contains the project plan

2. **Validate project plan structure**:
   - Must contain: Business objectives, target users, main features/capabilities
   - Can contain: Timeline, budget, constraints, success metrics
   - If structure is incomplete, guide user to add missing sections

### Step 2: Analyze Project and Identify Features

1. **Extract project context**:
   ```markdown
   - Project name and description
   - Business objectives
   - Target users/personas
   - Technical constraints
   - Success criteria
   - Timeline and budget
   ```

2. **Identify feature boundaries** using these criteria:
   
   **User-Centric Boundaries**:
   - Different user personas or roles
   - Separate user workflows or processes
   - Distinct user goals or outcomes
   - Different interaction patterns
   
   **Functional Boundaries**:
   - Core business capabilities
   - Separate data domains or entities
   - Distinct user interface areas
   - Independent business processes
   
   **Technical Boundaries**:
   - Separate system components or modules
   - Different data models or schemas
   - Independent API endpoints or services
   
   **Temporal Boundaries**:
   - MVP vs. enhancement features
   - Sequential user workflows
   - Dependency-driven ordering

3. **Generate feature candidates**:
   - Extract 5-12 potential features from the project plan
   - For each feature, determine:
     - Name and description
     - Business value (1-10 scale)
     - Technical complexity (1-10 scale)
     - Dependencies (list other features needed)
     - User stories (2-5 per feature)
     - Priority (P1-Critical, P2-High, P3-Medium, P4-Low)

### Step 3: Present Features for Review

Present all identified features in this format:

```markdown
# Feature Breakdown for [PROJECT NAME]

**Total Features Identified**: [N]
**Coverage Analysis**: [X]% of project requirements mapped to features

---

## Feature 1: [Feature Name] [Priority Badge]

**Business Value**: [X]/10 • **Complexity**: [Y]/10 • **Estimate**: [Z] weeks

### Description
[Brief description of what this feature does and why it's valuable]

### User Stories
- As a [user type], I want to [action] so that [benefit]
- As a [user type], I want to [action] so that [benefit]
- As a [user type], I want to [action] so that [benefit]

### Dependencies
- [Feature N] - [Reason for dependency]
- None (can be developed independently)

### Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]

### Scope Boundaries
**Includes**: [What IS in this feature]
**Excludes**: [What is NOT in this feature]

---

[Repeat for each feature]
```

### Step 4: Interactive Review (Optional)

If user wants interactive mode (default: yes), present each feature one at a time:

```
🔍 Feature Review: [N] of [TOTAL]

Feature: [Name] [Priority Badge]
Business Value: ████████░░ 8/10
Complexity:     ██████░░░░ 6/10

User Stories: [N] identified
Dependencies: [List or "None"]

Actions:
[A]pprove  [M]odify  [S]plit  [Me]rge  [D]elete  [De]tails  [Skip]  [Auto-approve all remaining]

Your choice:
```

**Actions**:
- **Approve**: Accept feature as-is
- **Modify**: Edit name, description, scope, or user stories
- **Split**: Break into 2-3 smaller features
- **Merge**: Combine with another feature (specify which)
- **Delete**: Remove feature (out of scope)
- **Details**: Show full feature details
- **Skip**: Defer decision
- **Auto-approve all**: Accept all remaining features without review

### Step 5: Validate Feature Breakdown

1. **Completeness Check**:
   - [ ] All project requirements covered by features
   - [ ] No significant gaps in functionality
   - [ ] All user personas addressed
   - [ ] Success criteria mapped to features

2. **Independence Check**:
   - [ ] Features can be developed independently (where possible)
   - [ ] Dependencies are clear and minimal
   - [ ] Features can be tested independently
   - [ ] No circular dependencies

3. **Quality Check**:
   - [ ] Each feature delivers clear business value
   - [ ] Feature boundaries are logical
   - [ ] Scope is manageable (2-4 weeks per feature)
   - [ ] User stories are well-defined

### Step 6: Generate Feature Breakdown Document

**ACTION REQUIRED**: Use `write_to_file` to create `docs/project-breakdown.md` with the following content:

```markdown
# Project Feature Breakdown: [PROJECT NAME]

**Created**: [DATE]
**Total Features**: [N]
**Estimated Timeline**: [X] weeks
**Priority Distribution**: [P1: N, P2: N, P3: N, P4: N]

## Project Context

**Business Objectives**:
[List from project plan]

**Target Users**:
[List personas]

**Success Criteria**:
[List project-level success criteria]

---

## Feature Summary

| ID | Feature Name | Priority | Value | Complexity | Estimate | Dependencies |
|----|--------------|----------|-------|------------|----------|--------------|
| F01 | [Name] | P1 | 9/10 | 6/10 | 3 weeks | None |
| F02 | [Name] | P1 | 8/10 | 7/10 | 4 weeks | F01 |
| ... | ... | ... | ... | ... | ... | ... |

---

## Feature Details

[Include full details for each feature from Step 3]

---

## Implementation Roadmap

### MVP (Minimum Viable Product)
**Timeline**: [X] weeks
**Features**: F01, F02, F03
**Goal**: [What the MVP delivers]

### Phase 2
**Timeline**: [X] weeks
**Features**: F04, F05, F06
**Goal**: [What Phase 2 adds]

### Phase 3
**Timeline**: [X] weeks
**Features**: F07, F08
**Goal**: [What Phase 3 completes]

---

## Dependency Graph

```
F01 (User Auth) ─┬─> F02 (Profile)
                 ├─> F03 (Admin Panel)
                 └─> F04 (Product Catalog)
                    
F04 (Product Catalog) ─┬─> F05 (Shopping Cart)
                       └─> F06 (Search)
                       
F05 (Shopping Cart) ──> F07 (Checkout)
```

---

## Next Steps

For each feature, run:
```bash
/speckit.specify [Feature Description from this document]
```

Example for F01:
```bash
/speckit.specify User Authentication System with email/password login, social OAuth, profile management, and role-based access control
```
```

### Step 7: Create Feature Description Files

**ACTION REQUIRED**: For each feature, use `write_to_file` to create `docs/features/feature-[ID]-description.md` (replace [ID] with F01, F02, etc.):

```markdown
# Feature [ID]: [Feature Name]

**Priority**: [P1/P2/P3/P4]
**Business Value**: [X]/10
**Estimated Effort**: [Y] weeks
**Dependencies**: [List or "None"]

## Feature Description

[Detailed description of the feature from Step 3]

## User Stories

[List all user stories]

## Success Criteria

[List success criteria]

## Scope

**Includes**:
- [What's in scope]

**Excludes**:
- [What's out of scope]

## Dependencies

[Describe any feature dependencies]

## Notes

[Any additional context, assumptions, or considerations]

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify [Paste complete feature description here]
```

Or copy this command:
```bash
/speckit.specify Feature [ID]: [Feature Name]. [Full description with user stories, success criteria, and scope]
```
```

### Step 8: Generate Quick Start Commands

**ACTION REQUIRED**: Use `write_to_file` to create `docs/features/quick-start.sh`:

```bash
#!/bin/bash
# Quick start commands for processing each feature through SpecKit

echo "🚀 SpecKit Feature Processing Quick Start"
echo "=========================================="
echo ""
echo "Process features in dependency order:"
echo ""

# Feature 1 (No dependencies)
echo "1️⃣ Feature F01: [Name]"
echo "   /speckit.specify [Description]"
echo ""

# Feature 2 (Depends on F01)
echo "2️⃣ Feature F02: [Name] (Depends on F01)"
echo "   /speckit.specify [Description]"
echo ""

# ... continue for all features

echo "📋 Or use batch processing:"
echo "   See docs/features/batch-process.md for automation script"
```

### Step 9: Report Results

Output a summary:

```markdown
## ✅ Project Breakdown Complete!

**Project**: [PROJECT NAME]
**Features Identified**: [N]
**Breakdown Document**: `docs/project-breakdown.md`

### Feature Summary

- **P1 Features** (Critical): [N] features, [X] weeks
- **P2 Features** (High): [N] features, [X] weeks  
- **P3 Features** (Medium): [N] features, [X] weeks
- **P4 Features** (Low): [N] features, [X] weeks

**Total Estimated Timeline**: [X] weeks

### Feature Files Created

- `docs/project-breakdown.md` - Master breakdown document
- `docs/features/feature-[ID]-description.md` - Individual feature descriptions
- `docs/features/quick-start.sh` - Quick command reference

### Next Steps

1. **Review the breakdown**: Open `docs/project-breakdown.md`
2. **Start with MVP features**: Process P1 features first
3. **Process each feature**: Run `/speckit.specify` for each feature:
   ```
   /speckit.specify [Feature description from docs/features/feature-01-description.md]
   ```
4. **Follow the roadmap**: Use dependency graph to determine order

### Recommended Processing Order

Based on dependencies, process features in this order:
1. [Feature 1] - No dependencies
2. [Feature 2] - Depends on Feature 1
3. [Feature 3] - Depends on Feature 1
...

---

**Ready to create your first feature spec?** 
Run: `/speckit.specify` with Feature F01's description!
```

## Guidelines

### Feature Sizing

- **Ideal feature**: 2-4 weeks of development effort
- **Too small**: < 1 week (consider merging)
- **Too large**: > 4 weeks (consider splitting)

### Feature Independence

Aim for **70-80% independent features**:
- Most features should have 0-1 dependencies
- Create shared infrastructure features for common dependencies
- Avoid circular dependencies

### Priority Assignment

- **P1 (Critical)**: MVP features, blocking dependencies, core business value
- **P2 (High)**: Important features, significant user value, phase 2
- **P3 (Medium)**: Nice-to-have, enhancement features
- **P4 (Low)**: Future considerations, low immediate value

### Quality Gates

Before finalizing breakdown:
- [ ] Every feature has clear business value
- [ ] User stories are specific and testable
- [ ] Dependencies are documented
- [ ] Scope boundaries are explicit
- [ ] Success criteria are measurable

## Common Patterns

### Good Feature Boundaries

✅ **User Authentication System**
- Includes: Login, registration, password reset, profile management
- Clear user value, complete workflow

✅ **Product Catalog with Search**
- Includes: Product listing, categories, search, filters
- Complete user journey for product discovery

✅ **Shopping Cart & Checkout**
- Includes: Add to cart, cart management, checkout flow
- End-to-end purchase workflow

### Anti-Patterns to Avoid

❌ **Technical Layer Features**
- "Database Layer", "API Gateway", "Authentication Service"
- Focus on user value, not technical components

❌ **Overly Granular**
- "Login Button", "Registration Form", "Password Field"
- Too small, should be combined

❌ **Too Broad**
- "Complete E-commerce Platform", "Entire Admin System"
- Too large, needs breaking down

## Error Handling

- **No project plan found**: Guide user to create one with required sections
- **Unclear feature boundaries**: Ask clarifying questions about user workflows
- **Circular dependencies**: Identify and help resolve
- **Coverage gaps**: Highlight missing functionality from project plan
- **Scope creep**: Flag features that seem out of scope

## Integration with Existing Workflows

After breakdown, each feature flows through:

```
speckit.breakdown
    ↓
    Feature F01 → /speckit.specify → /speckit.clarify → /speckit.plan → /speckit.tasks → /speckit.implement
    Feature F02 → /speckit.specify → /speckit.clarify → /speckit.plan → /speckit.tasks → /speckit.implement
    Feature F03 → /speckit.specify → /speckit.clarify → /speckit.plan → /speckit.tasks → /speckit.implement
    ...
```

Each feature becomes independently specifiable and implementable!
